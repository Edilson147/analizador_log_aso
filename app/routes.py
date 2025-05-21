import os
from flask import current_app, Blueprint, request, render_template, redirect
from .log_parser import parse_log_file
from flask import Flask, request, jsonify
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
    if accion == 'actualizar':
        if tipo == 'apache_access':
            cur.execute("TRUNCATE TABLE apache_access_logs")
            app.mysql.connection.commit()
            importar_apache_access()
            cur.execute("SELECT * FROM apache_access_logs")
            logs = cur.fetchall()
        elif tipo == 'apache_error':
            cur.execute("TRUNCATE TABLE apache_error_logs")
            app.mysql.connection.commit()
            importar_apache_error()
            cur.execute("SELECT * FROM apache_error_logs")
            logs = cur.fetchall()
        elif tipo == 'ftp':
            cur.execute("TRUNCATE TABLE ftp_logs")
            app.mysql.connection.commit()
            importar_ftp_logs()
            cur.execute("SELECT fecha, usuario, pid_id, ip, tipo_accion, descripcion FROM ftp_logs ")
            logs = cur.fetchall()
            print("hola mundo")
        else:
            logs = []
    elif accion=='analizar':
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
        termino_buscado= request.form.get('texto_ingresado','').strip()
        if tipo == 'apache_access'and termino_buscado:
            query = """
                SELECT * FROM apache_access_logs
                WHERE 
                    ip LIKE %s OR
                    usuario LIKE %s OR
                    metodo LIKE %s OR
                    recurso LIKE %s OR
                    protocolo LIKE %s OR
                    user_agent LIKE %s OR
                    codigo_estado LIKE %s OR
                    tamano_respuesta LIKE %s 

            """
            like_term = f"%{termino_buscado}%"
            cur.execute(query, (like_term, like_term, like_term, like_term, like_term, like_term,like_term, like_term))
            logs = cur.fetchall()
            cur.close()
        elif tipo == 'apache_error' and termino_buscado :
            query = """
                SELECT * FROM apache_error_logs
                WHERE 
                    nivel LIKE %s OR
                    modulo LIKE %s OR
                    pid_id LIKE %s OR
                    codigo_mensaje LIKE %s OR
                    mensaje LIKE %s

            """
            like_term = f"%{termino_buscado}%"
            cur.execute(query, (like_term, like_term, like_term, like_term, like_term))
            logs = cur.fetchall()
            cur.close()
        elif tipo == 'ftp' and termino_buscado:
            query = """
                SELECT * FROM ftp_logs
                WHERE 
                    usuario LIKE %s OR
                    pid_id LIKE %s OR
                    ip LIKE %s OR
                    tipo_accion LIKE %s OR
                    descripcion LIKE %s
            """
            like_term = f"%{termino_buscado}%"
            cur.execute(query, (like_term, like_term, like_term, like_term, like_term))
            logs = cur.fetchall()
            cur.close()
            
        else:
             logs = []
        
    else:    
        logs = []
    return render_template("logs.html", logs=logs, tipo_seleccionado=tipo)

@bp.route('/api/filtros', methods=['POST'])
def filtrar():
    datos = request.get_json()
    cur = app.mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    # Extraer los filtros enviados
    fecha = datos.get('fecha')
    fecha_inicio = datos.get('fechaInicio')
    fecha_fin = datos.get('fechaFin')
    hora = datos.get('hora')
    tipo = datos.get('select_categoria')
    print(tipo)
    categorias_seleccionadas = datos.get('categorias_selecionadas')
    print(datos)
    if tipo == 'apache_access':
       sql = construir_sql_access(datos)
       cur.execute(sql)
       logs = cur.fetchall()
       app.mysql.connection.commit()
       print(sql)
    elif tipo == 'apache_error':
       sql = construir_sql_error(datos)
       cur.execute(sql)
       logs = cur.fetchall()
       app.mysql.connection.commit()
       print(sql)
    elif tipo =='ftp':
       sql = construir_sql_ftp(datos)
       cur.execute(sql)
       logs = cur.fetchall()
       app.mysql.connection.commit()
       print(sql)
    else:
       logs=datos
    # Aquí iría tu lógica de filtrado (consultar BD, aplicar filtros, etc.)
    # Simulación de respuesta:
    resultados = {
        "mensaje": "Filtros recibidos correctamente",
        "datos_filtrados": logs,
    }
    return jsonify(resultados)

def construir_sql_error(filtros):
    condiciones = []

    # Filtros por categorías seleccionadas
    categorias = filtros.get('categorias_selecionadas', {})

    nivel = categorias.get('Nivel', [])
    if nivel:
        nivel_str = "', '".join(nivel)
        condiciones.append(f"nivel IN ('{nivel_str}')")

    modulo = categorias.get('Modulo', [])
    if modulo:
        modulo_str = "', '".join(modulo)
        condiciones.append(f"modulo IN ('{modulo_str}')")

    # Filtro por fecha exacta
    fecha = filtros.get('fecha')
    if fecha:
        condiciones.append(f"DATE(fecha) = '{fecha}'")

    # Filtro por rango de fechas
    fecha_inicio = filtros.get('fechaInicio')
    fecha_fin = filtros.get('fechaFin')
    if fecha_inicio and fecha_fin:
        condiciones.append(f"fecha BETWEEN '{fecha_inicio} 00:00:00' AND '{fecha_fin} 23:59:59'")

    # Filtro por hora
    hora = filtros.get('hora')
    if hora:
        condiciones.append(f"TIME(fecha) = '{hora}:00'")

    # Armar la consulta
    sql = "SELECT * FROM apache_error_logs"
    if condiciones:
        sql += " WHERE " + " AND ".join(condiciones)
    return sql
def construir_sql_ftp(filtros):
    condiciones = []

    # Filtros por categorías seleccionadas
    categorias = filtros.get('categorias_selecionadas', {})

    tipo_accion = categorias.get('Tipo accion', [])
    if tipo_accion:
        tipo_accion_str = "', '".join(tipo_accion)
        condiciones.append(f"tipo_accion IN ('{tipo_accion_str}')")

    # Filtro por fecha exacta
    fecha = filtros.get('fecha')
    if fecha:
        condiciones.append(f"DATE(fecha) = '{fecha}'")

    # Filtro por rango de fechas
    fecha_inicio = filtros.get('fechaInicio')
    fecha_fin = filtros.get('fechaFin')
    if fecha_inicio and fecha_fin:
        condiciones.append(f"fecha BETWEEN '{fecha_inicio} 00:00:00' AND '{fecha_fin} 23:59:59'")

    # Filtro por hora
    hora = filtros.get('hora')
    if hora:
        condiciones.append(f"TIME(fecha) = '{hora}:00'")

    # Armar la consulta
    sql = "SELECT * FROM ftp_logs"
    if condiciones:
        sql += " WHERE " + " AND ".join(condiciones)
    return sql
def construir_sql_access(filtros):
    condiciones = []

    # Filtros por categorías seleccionadas
    categorias = filtros.get('categorias_selecionadas', {})

    solicitud = categorias.get('Solicitud', [])
    if solicitud:
        metodos = "', '".join(solicitud)
        condiciones.append(f"metodo IN ('{metodos}')")

    codigos = categorias.get('Codigo Estado', [])
    if codigos:
        codigos_str = "', '".join(codigos)
        condiciones.append(f"codigo_estado IN ('{codigos_str}')")

    navegadores = categorias.get('Codigo Estado', [])
    if navegadores:
        navegadores_ua = [f"user_agent LIKE '%{ua}%'" for ua in navegadores]
        condiciones.append("(" + " OR ".join(navegadores_ua) + ")")
    # Filtro por fecha exacta
    fecha = filtros.get('fecha')
    if fecha:
        condiciones.append(f"DATE(fecha) = '{fecha}'")

    # Filtro por rango de fechas
    fecha_inicio = filtros.get('fechaInicio')
    fecha_fin = filtros.get('fechaFin')
    if fecha_inicio and fecha_fin:
        condiciones.append(f"fecha BETWEEN '{fecha_inicio} 00:00:00' AND '{fecha_fin} 23:59:59'")

    # Filtro por hora
    hora = filtros.get('hora')
    if hora:
        condiciones.append(f"TIME(fecha) = '{hora}:00'")

    # Armar la consulta
    sql = "SELECT * FROM apache_access_logs"
    if condiciones:
        sql += " WHERE " + " AND ".join(condiciones)

    return sql
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
    
    try:
        with open('/var/log/apache2/access_log', 'r', encoding='utf-8', errors='ignore') as f:
            logs = parse_log_file(f, tipo='apache')
      
        cur = app.mysql.connection.cursor()
        for log in logs:
            cur.execute("""
                INSERT INTO apache_access_logs 
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
                INSERT INTO apache_error_logs (fecha, nivel, modulo, pid_id, codigo_mensaje, mensaje)
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
    INSERT INTO ftp_logs (fecha, usuario, pid_id, ip, tipo_accion, descripcion)
    VALUES (%s, %s, %s, %s, %s, %s)
""", (log['fecha'], log['usuario'],log['pid_id'], log['ip'], log['tipo_accion'], log['descripcion']))
        app.mysql.connection.commit()
        return "Logs de FTP importados correctamente."
    except Exception as e:
        return f"Error al importar: {str(e)}"
