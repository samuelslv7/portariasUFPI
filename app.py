from flask import Flask, render_template, request, send_from_directory
import sqlite3
import pandas as pd
import os

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "db", "contratos_ufpi.db")
PDF_FOLDER = os.path.join(BASE_DIR, "static", "portarias")

#DB_PATH = "./db/contratos_ufpi.db"
#PDF_FOLDER = os.path.join("static", "portarias")


def formatar_data(valor):
    if pd.isna(valor) or valor == "":
        return "N/A"
    try:
        return pd.to_datetime(valor).strftime("%d/%m/%Y")
    except:
        return str(valor)


@app.route("/download/<filename>")
def download_file(filename):
    # Envia o arquivo da pasta static/pdfs para o usuário
    return send_from_directory(PDF_FOLDER, filename)


@app.route("/", methods=["GET", "POST"])
def index():
    resultados = []
    siape_buscado = ""

    if request.method == "POST":
        siape_buscado = request.form.get("siape", "").strip()
        if siape_buscado:
            conn = sqlite3.connect(DB_PATH)
            # Buscar os dados no banco
            query = "SELECT * FROM contratos WHERE siape = ? ORDER BY ano_aba"
            df = pd.read_sql_query(query, conn, params=(siape_buscado,))
            conn.close()

            if not df.empty:
                df["data"] = df["data"].apply(formatar_data)
                resultados = df.to_dict("records")
                for row in resultados:
                    # Nome esperado do arquivo (Ex: PORTARIA 120-2017 CT 19-2013.pdf)
                    nome_arquivo = f"PORTARIA {row['portaria'].replace('/', '-')} CT {row['contrato'].replace('/', '-')}.pdf"
                    caminho_real = os.path.join(PDF_FOLDER, nome_arquivo)

                    # Adicionamos uma flag para o HTML saber se mostra o link ou não
                    row["pdf_disponivel"] = os.path.exists(caminho_real)
                    row["nome_arquivo"] = nome_arquivo
    return render_template("index.html", resultados=resultados, siape=siape_buscado)


if __name__ == "__main__":
    # migrar_excel_para_sqlite_ajustado("portarias.xlsx", DB_PATH)
    app.run(debug=True, host="0.0.0.0", port=5000)
