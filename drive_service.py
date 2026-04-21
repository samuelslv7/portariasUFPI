import os
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build


def obter_servico_drive():
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