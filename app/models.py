# app/models.py
from flask_mysqldb import MySQL

def init_db(mysql):
    cursor = mysql.connection.cursor()

    # Tabla 1: Apache Access Logs
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS apache_access_logs (
        id INT AUTO_INCREMENT PRIMARY KEY,
        fecha DATETIME, 
        ip VARCHAR(45),
        usuario VARCHAR(100),
        metodo VARCHAR(10),
        recurso TEXT,
        protocolo VARCHAR(10),
        codigo_estado INT,
        tamano_respuesta INT,
        user_agent TEXT,
        creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # Tabla 2: Apache Error Logs
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS apache_error_logs (
        id INT AUTO_INCREMENT PRIMARY KEY,
        fecha DATETIME,
        nivel VARCHAR(50),
        modul0 VARCHAR(100),
        pid_id INT,
        codigo_mensaje VARCHAR(20),
        mensaje TEXT,
        creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # Tabla 3: FTP Logs (vsftpd)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS ftp_logs (
        id INT AUTO_INCREMENT PRIMARY KEY,
        fecha DATETIME,
        usuario VARCHAR(100),
        pid_id VARCHAR(100),
        ip VARCHAR(45),
        tipo_accion VARCHAR(50),
        descripcion TEXT,
        creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    mysql.connection.commit()
    cursor.close()

