import os
from flask import current_app, Blueprint, request, render_template, redirect
from .log_parser import parse_log_file
from flask import current_app as app
import MySQLdb.cursors


bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    return render_template('logs.html')

@bp.route('/logs', methods=['POST'])
def logs():
    tipo = request.form.get('tipo')  # 'apache_access', 'apache_error' o 'ftp'
    cur = app.mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    accion = request.form.get('accion')
    if accion == 'analizar':
        if tipo == 'apache_access':
            print("hola mundo")
            importar_apache_access()
            cur.execute("SELECT * FROM apache_access_logs")
            logs = cur.fetchall()
        elif tipo == 'apache_error':
            importar_apache_error()
            cur.execute("SELECT * FROM apache_error_logs")
            logs = cur.fetchall()
        elif tipo == 'ftp':
            importar_ftp_logs()
            cur.execute("SELECT fecha, usuario, pid_id, ip, tipo_accion, descripcion FROM ftp_logs ")
            logs = cur.fetchall()
            print("hola mundo")
        else:
            logs = []
    elif accion=='actualizar':
        if tipo == 'apache_access':
            cur.execute("SELECT * FROM apache_access_logs ")
            logs = cur.fetchall()
        elif tipo == 'apache_error':
            cur.execute("SELECT * FROM apache_error_logs ")
            logs = cur.fetchall()
        elif tipo == 'ftp':
            cur.execute("SELECT fecha, usuario, pid_id, ip, tipo_accion, descripcion FROM ftp_logs")
            logs = cur.fetchall()
        else:
            logs = []
    elif accion=='buscador':
        texto_buscado= request.form.get('texto_ingresado')
        print(texto_buscado)
        logs = []
    else:    
        logs = []
    return render_template("logs.html", logs=logs, tipo_seleccionado=tipo)



@bp.route('/ver_logs', methods=['POST','GET'])
def ver_logs():
    if request.method == 'POST':
        tipo = request.form.get('tipo')  # 'apache_access', 'apache_error' o 'ftp'
        cur = app.mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        if tipo == 'apache_access':           
            cur.execute("SELECT ip, fecha, FROM apache_access_logs")
            logs = cur.fetchall()
            cur.close()
            
        elif tipo == 'apache_error':           
            cur.execute("SELECT * FROM apache_error_logs")
            logs = cur.fetchall()
        elif tipo == 'ftp':
            cur.execute("SELECT fecha, usuario, pid_id, ip, tipo_accion, descripcion FROM ftp_logs")
            logs = cur.fetchall()
        else:
            print('hola mundo')
    else:
       return render_template('ver_logs.html')  
        
    


def importar_apache_access():
    print("hola mundo")
    try:
        with open('/var/log/apache2/access_log', 'r', encoding='utf-8', errors='ignore') as f:
            print("hola mundo")
            logs = parse_log_file(f, tipo='apache')
      
        cur = app.mysql.connection.cursor()
        for log in logs:
            cur.execute("""
                INSERT IGNORE INTO apache_access_logs 
                (fecha, ip, usuario, metodo, recurso, protocolo, codigo_estado, tamano_respuesta, user_agent)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                log['fecha'], log['ip'], log['usuario'], log['metodo'],
                log['recurso'], log['protocolo'], log['codigo_estado'],
                log['tamano_respuesta'], log['user_agent']
            ))
        app.mysql.connection.commit()
        return "Logs de Apache Access importados correctamente."
    except Exception as e:
        return f"Error al importar: {str(e)}"


def importar_apache_error():
    try:
        with open('/var/log/apache2/error_log', 'r', encoding='utf-8', errors='ignore') as f:
            logs = parse_log_file(f, tipo='apache_error')  # Este tipo deberás definir si quieres parsear errores
     
        cur = app.mysql.connection.cursor()
        for log in logs:
            cur.execute("""
                INSERT IGNORE INTO apache_error_logs (fecha, nivel, modulo, pid_id, codigo_mensaje, mensaje)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (log['fecha'], log['nivel'], log['modulo'], log['pid_id'], log['codigo_mensaje'], log['mensaje']))
        app.mysql.connection.commit()
        return "Logs de Apache Error importados correctamente."
    except Exception as e:
        return f"Error al importar: {str(e)}"


def importar_ftp_logs():
    try:
        with open('/var/log/vsftpd.log', 'r', encoding='utf-8', errors='ignore') as f:
            logs = parse_log_file(f, tipo='ftp')
        
        cur = app.mysql.connection.cursor()
        for log in logs:
          cur.execute("""
    INSERT IGNORE INTO ftp_logs (fecha, usuario, pid_id, ip, tipo_accion, descripcion)
    VALUES (%s, %s, %s, %s, %s, %s)
""", (log['fecha'], log['usuario'],log['pid_id'], log['ip'], log['tipo_accion'], log['descripcion']))
        app.mysql.connection.commit()
        return "Logs de FTP importados correctamente."
    except Exception as e:
        return f"Error al importar: {str(e)}"
