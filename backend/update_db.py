import sqlite3

DB_PATH = "seguros.db"

def añadir_columnas():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        cursor.execute("ALTER TABLE polizas ADD COLUMN email_contacto TEXT")
        print("Columna email_contacto añadida.")
    except:
        print("email_contacto ya existe.")

    try:
        cursor.execute("ALTER TABLE polizas ADD COLUMN notificacion_enviada BOOLEAN DEFAULT 0")
        print("Columna notificacion_enviada añadida.")
    except:
        print("notificacion_enviada ya existe.")

    conn.commit()
    conn.close()

if __name__ == "__main__":
    añadir_columnas()
