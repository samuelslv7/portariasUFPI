import sqlite3
from drive_service import *

def sincronizar_links_drive():
    service = obter_servico_drive() # Sua conexão com Google Drive
    id_pasta = "1bMndtRFMbucRqEqjJK3Hl3LRT9N-DAcc"
    
    # 1. Busca arquivos no Drive
    results = service.files().list(
        q=f"'{id_pasta}' in parents and trashed = false",
        fields="files(name, webViewLink)"
    ).execute()
    arquivos_drive = results.get('files', [])

    conn = sqlite3.connect("./db/contratos_ufpi.db")
    cursor = conn.cursor()

    # Resetamos os links para atualizar com as novas informações
    cursor.execute("UPDATE contratos SET link_drive = NULL")

    for arquivo in arquivos_drive:
        # Ex: "PORTARIA 110-2017 CT 05-2015.pdf"
        nome_original = arquivo['name'].upper()
        link = arquivo['webViewLink']
        
        # Criamos uma versão "normalizada" do nome do arquivo 
        # (trocando hifens por barras para bater com o BD)
        nome_normalizado = nome_original.replace('-', '/')

        # O SQL agora checa se a portaria E o contrato estão no nome
        # Usamos COALESCE no contrato para o caso de ele ser NULL no banco
        cursor.execute("""
            UPDATE contratos 
            SET link_drive = ? 
            WHERE ? LIKE '%' || portaria || '%'
              AND (? LIKE '%' || COALESCE(contrato, '') || '%' OR contrato IS NULL)
        """, (link, nome_normalizado, nome_normalizado))
    
    conn.commit()
    conn.close()
    print(f"Sincronização finalizada. {len(arquivos_drive)} arquivos processados.")

if __name__ == "__main__":
    sincronizar_links_drive()