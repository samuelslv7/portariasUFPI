import os
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build

def obter_servico_drive():
    # 1. Tenta ler a variável de ambiente da Vercel
    # 2. Se não existir (local), tenta ler o arquivo credentials.json
    creds_raw = os.environ.get('GOOGLE_CREDENTIALS')
    
    if creds_raw:
        info = json.loads(creds_raw)
    else:
        with open('credentials.json', 'r') as f:
            info = json.load(f)

    scopes = ['https://www.googleapis.com/auth/drive.readonly']
    creds = service_account.Credentials.from_service_account_info(info, scopes=scopes)
    return build('drive', 'v3', credentials=creds)

def buscar_pdf_drive(nome_portaria):
    service = obter_servico_drive()
    nome_busca = nome_portaria.replace('/', '-')
    
    # Substitua pelo ID da sua pasta (fica na URL do navegador quando você abre a pasta)
    id_pasta = "11bMndtRFMbucRqEqjJK3Hl3LRT9N-DAcc" 
    
    query = f"name contains '{nome_busca}' and '{id_pasta}' in parents and trashed = false"
    results = service.files().list(q=query, fields="files(id, name, webViewLink)").execute()
    items = results.get('files', [])
    
    return items[0]['webViewLink'] if items else None