import sqlite3
import pandas as pd
import os


def migrar_excel_para_sqlite(caminho_excel, caminho_db):
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
            lotacao TEXT
        )
    """
    )

    abas = pd.read_excel(caminho_excel, sheet_name=None, header=1)

    total_registros = 0

    for nome_aba, df in abas.items():
        # 1. Limpeza de colunas: remover espaços e converter para minúsculas
        # Isso ajuda se em uma aba estiver "Função" e na outra "função"
        df.columns = [str(c).lower().strip() for c in df.columns]

        # 2. Mapeamento de colunas (Garante que os nomes batam com o Banco de Dados)
        # Se na planilha a coluna chama 'função', o código abaixo renomeia para 'funcao'
        mapeamento = {"função": "funcao", "lotação": "lotacao"}
        df = df.rename(columns=mapeamento)

        # 3. Filtrar apenas as colunas que existem no banco para evitar erro de inserção
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
        # Mantém apenas as colunas que realmente existem no DataFrame atual
        df = df[[c for c in colunas_validas if c in df.columns]]

        # 4. Adicionar a identificação da Aba
        df["ano_aba"] = nome_aba

        # 5. Tratar SIAPE como string limpa
        if "siape" in df.columns:
            df["siape"] = (
                df["siape"].astype(str).str.replace(".0", "", regex=False).str.strip()
            )
        
        # No seu loop de migração das abas:
        df['contrato'] = df['contrato'].fillna("Não Informado")
        df['empresa'] = df['empresa'].fillna("Não Informado")
        df['portaria'] = df['portaria'].fillna("S/N")

        df.to_sql("contratos", conn, if_exists="append", index=False)
        total_registros += len(df)
        print(f"Aba {nome_aba} processada: {len(df)} linhas inseridas.")

    conn.commit()
    conn.close()
    if os.path.exists("contratos_ufpi.db"):
        os.remove("contratos_ufpi.db")
    print(f"\nSucesso! {total_registros} registros migrados para o SQLite.")


pasta_DB = "./db"
if not os.path.exists(pasta_DB):
    os.makedirs(pasta_DB, exist_ok=True)
migrar_excel_para_sqlite("contratos.xlsx", pasta_DB + "/contratos_ufpi.db")
