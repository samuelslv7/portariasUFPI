import sqlite3
from drive_service import obter_servico_drive

def sincronizar_links_drive():
    service = obter_servico_drive()

    ID_PASTA_RAIZ = "1bMndtRFMbucRqEqjJK3Hl3LRT9N-DAcc"
    
    query_pastas = f"'{ID_PASTA_RAIZ}' in parents and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
    pastas_results = service.files().list(q=query_pastas, fields="files(id, name)").execute()
    subpastas = pastas_results.get('files', [])
    
    ids_para_buscar = [ID_PASTA_RAIZ] + [f['id'] for f in subpastas]
    
    conn = sqlite3.connect("./db/contratos_ufpi.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE contratos SET link_drive = NULL")

    print(f"Buscando em {len(ids_para_buscar)} pastas diferentes...")

    for pasta_id in ids_para_buscar:
        # Busca os arquivos dentro de cada subpasta
        query_files = f"'{pasta_id}' in parents and trashed = false"
        results = service.files().list(q=query_files, fields="files(name, webViewLink)").execute()
        arquivos_drive = results.get('files', [])

        for arquivo in arquivos_drive:
            nome_original = arquivo['name'].upper()
            link = arquivo['webViewLink']
            nome_normalizado = nome_original.replace('-', '/')

            cursor.execute("""
                UPDATE contratos 
                SET link_drive = ? 
                WHERE ? LIKE '%' || portaria || '%'
                  AND (? LIKE '%' || COALESCE(contrato, '') || '%' OR contrato IS NULL)
            """, (link, nome_normalizado, nome_normalizado))
    
    conn.commit()
    conn.close()
    print("Sincronização completa em todas as pastas de ano!")

if __name__ == "__main__":
    sincronizar_links_drive()
