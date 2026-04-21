import sqlite3
import pandas as pd
import os

def migrar_excel_para_sqlite(caminho_excel, caminho_db):
    # --- Remover o banco de dados antigo antes de começar ---
    if os.path.exists(caminho_db):
        os.remove(caminho_db)
        print(f"Banco de dados antigo removido para evitar duplicados.")

    conn = sqlite3.connect(caminho_db)
    cursor = conn.cursor()

    # Criar a tabela
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS contratos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ano_aba TEXT,
            contrato TEXT,
            empresa TEXT,
            portaria TEXT,
            data TEXT,
            funcao TEXT,
            nome TEXT,
            siape TEXT,
            lotacao TEXT,
            link_drive TEXT
        )
    """
    )

    abas = pd.read_excel(caminho_excel, sheet_name=None, header=1)
    total_registros = 0

    for nome_aba, df in abas.items():
        df.columns = [str(c).lower().strip() for c in df.columns]

        mapeamento = {"função": "funcao", "lotação": "lotacao"}
        df = df.rename(columns=mapeamento)

        colunas_validas = [
            "contrato",
            "empresa",
            "portaria",
            "data",
            "funcao",
            "nome",
            "siape",
            "lotacao",
        ]

        df = df[[c for c in colunas_validas if c in df.columns]]
        df["ano_aba"] = nome_aba

        # Tratar SIAPE como string limpa
        if "siape" in df.columns:
            df["siape"] = (
                df["siape"].astype(str).str.replace(".0", "", regex=False).str.strip()
            )

        # Preencher valores nulos para evitar erros de busca
        df['contrato'] = df['contrato'].fillna("Não Informado")
        df['empresa'] = df['empresa'].fillna("Não Informado")
        df['portaria'] = df['portaria'].fillna("S/N")

        df.to_sql("contratos", conn, if_exists="append", index=False)
        total_registros += len(df)
        #print(f"Aba {nome_aba} processada: {len(df)} linhas inseridas.")

    conn.commit()
    conn.close()
    print(f"Sucesso! {total_registros} registros migrados para o SQLite\nAtualizar link com o sync_drive.py")


pasta_DB = "./db"
if not os.path.exists(pasta_DB):
    os.makedirs(pasta_DB, exist_ok=True)

migrar_excel_para_sqlite("contratos.xlsx", os.path.join(pasta_DB, "contratos_ufpi.db"))