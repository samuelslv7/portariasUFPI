import os
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build

id_pasta = "1bMndtRFMbucRqEqjJK3Hl3LRT9N-DAcc"


def mapear_arquivos_drive(service):
    # Busca TODOS os arquivos daquela pasta de uma vez (limite de 1000)
    query = f"'{id_pasta}' in parents and trashed = false"
    results = (
        service.files()
        .list(q=query, fields="files(id, name, webViewLink)", pageSize=1000)
        .execute()
    )

    # Cria um dicionário: {'120-2017': 'link...', '110-2017': 'link...'}
    # Removemos a extensão .pdf do nome para facilitar o cruzamento
    mapa = {
        f["name"].lower().replace(".pdf", ""): f["webViewLink"]
        for f in results.get("files", [])
    }
    return mapa


def obter_servico_drive():
    # 1. Tenta ler a variável de ambiente da Vercel
    # 2. Se não existir (local), tenta ler o arquivo credentials.json
    creds_raw = os.environ.get("GOOGLE_CREDENTIALS")

    if creds_raw:
        info = json.loads(creds_raw)
    else:
        try:
            with open("credentials.json", "r") as f:
                info = json.load(f)
        except FileNotFoundError:
            print("Erro: O arquivo não foi encontrado.")
        except Exception as e:
            print(f"Ocorreu um erro inesperado: {e}")

    scopes = ["https://www.googleapis.com/auth/drive.readonly"]
    creds = service_account.Credentials.from_service_account_info(info, scopes=scopes)
    return build("drive", "v3", credentials=creds)


def buscar_pdf_drive(nome_portaria):
    service = obter_servico_drive()

    try:
        pasta = service.files().get(fileId=id_pasta, fields="name").execute()
        print(f"Conectado com sucesso à pasta: {pasta['name']}")
    except Exception as e:
        print(f"Erro de permissão ou ID inválido: {e}")

    query = f"name contains '{nome_portaria}' and '{id_pasta}' in parents and trashed = false"
    results = (
        service.files().list(q=query, fields="files(id, name, webViewLink)").execute()
    )
    items = results.get("files", [])

    return items[0]["webViewLink"] if items else None
