from flask import Flask, render_template, request, send_from_directory
import sqlite3
import pandas as pd
import os
from urllib.parse import unquote
from drive_service import *

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "db", "contratos_ufpi.db")
PDF_FOLDER = os.path.join(BASE_DIR, "static", "portarias")


def formatar_data(valor):
    if pd.isna(valor) or valor == "":
        return "N/A"
    try:
        return pd.to_datetime(valor).strftime("%d/%m/%Y")
    except:
        return str(valor)


@app.route("/download/<path:filename>")
def download_file(filename):
    # Converte %20 de volta para espaços reais
    nome_limpo = unquote(filename)

    return send_from_directory(PDF_FOLDER, nome_limpo, as_attachment=False)


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

            if resultados:
                service = obter_servico_drive()
                # Buscamos oW mapa da pasta uma única vez por requisição
                mapa_pdfs = mapear_arquivos_drive(service)

                for row in resultados:
                    # Cruzamos os dados localmente (muito rápido)
                    nome_chave = row["portaria"].replace("/", "-").lower()
                    row["link_pdf"] = mapa_pdfs.get(nome_chave)
                    row["pdf_disponivel"] = True if row["link_drive"] else False
                    print(row['pdf_disponivel'])
                    print(row['link_drive'])

    return render_template("index.html", resultados=resultados, siape=siape_buscado)


@app.route("/debug")
def debug_files():
    import os

    # Lista o que tem na pasta static/pdfs
    base_dir = os.path.dirname(os.path.abspath(__file__))
    pdf_path = os.path.join(base_dir, "static", "portarias")

    files = []
    if os.path.exists(pdf_path):
        files = os.listdir(pdf_path)

    return {
        "diretorio_atual": base_dir,
        "caminho_buscado": pdf_path,
        "pasta_existe": os.path.exists(pdf_path),
        "arquivos_na_pasta": files,
    }


if __name__ == "__main__":
    # migrar_excel_para_sqlite_ajustado("portarias.xlsx", DB_PATH)
    app.run(debug=True, host="0.0.0.0", port=5000)
