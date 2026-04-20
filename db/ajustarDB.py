import sqlite3

def adicionar_coluna_link():
    conn = sqlite3.connect("./db/contratos_ufpi.db")
    cursor = conn.cursor()
    try:
        cursor.execute("ALTER TABLE contratos ADD COLUMN link_drive TEXT")
        conn.commit()
        print("Coluna link_drive adicionada com sucesso!")
    except sqlite3.OperationalError:
        print("A coluna já existe.")
    conn.close()

adicionar_coluna_link()