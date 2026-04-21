from flask import Flask, render_template, request
import sqlite3
import pandas as pd
import os

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "db", "contratos_ufpi.db")


def formatar_data(valor):
    if pd.isna(valor) or valor == "":
        return "N/A"
    try:
        return pd.to_datetime(valor).strftime("%d/%m/%Y")
    except:
        return str(valor)


@app.route("/", methods=["GET", "POST"])
def index():
    resultados = []
    siape_buscado = ""

    if request.method == "POST":
        siape_buscado = request.form.get("siape", "").strip()
        if siape_buscado:
            conn = sqlite3.connect(DB_PATH)
            # Buscar os dados no banco
            query = "SELECT * FROM contratos WHERE siape = ?"
            df = pd.read_sql_query(query, conn, params=(siape_buscado,))
            conn.close()

            if not df.empty:
                df["data"] = df["data"].apply(formatar_data)
                resultados = df.to_dict("records")

            if resultados:
                for row in resultados:
                    link = row.get('link_drive')
                    if link and str(link).lower() != 'nan':
                        row['pdf_disponivel'] = True
                        row['link_pdf'] = link
                    else:
                        row['pdf_disponivel'] = False
                        row['link_pdf'] = None
                        
                    #row["pdf_disponivel"] = True if row["link_drive"] else False

    return render_template("index.html", resultados=resultados, siape=siape_buscado)

@app.route('/debug-img')
def debug_img():
    # Caminho onde as imagens deveriam estar
    caminho = os.path.join(app.root_path, 'static', 'img')
    try:
        if os.path.exists(caminho):
            arquivos = os.listdir(caminho)
            return f"Arquivos encontrados em {caminho}: <br> " + "<br>".join(arquivos)
        else:
            return f"Erro: A pasta {caminho} NÃO EXISTE no servidor da Vercel."
    except Exception as e:
        return f"Erro ao acessar pasta: {str(e)}"


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
