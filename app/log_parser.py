# log_analyzer/app/log_parser.py
import re
from datetime import datetime

# Apache access log format: IP - - [fecha] "metodo recurso protocolo" codigo tamaño
apache_access_regex = r'(?P<ip>\S+) - (?P<usuario>\S+) \[(?P<fecha>[^\]]+)\] "(?P<metodo>\S+) (?P<recurso>\S+) (?P<protocolo>[^"]+)" (?P<codigo>\d{3}) (?P<tamano>\d+|-)+ "[^"]*" "(?P<user_agent>[^"]+)"'

# Apache error log format: [fecha] [nivel] [cliente ...] mensaje
# Regex completas_error
regex_completo = r'^\[(?P<fecha>[^\]]+)\] \[(?P<modulo>[^:\]]+):(?P<nivel>[^\]]+)\](?: \[pid (?P<pid>\d+)\])? (?P<mensaje>.+)'
regex_sin_fecha = r'^\[(?P<modulo>[^:\]]+):(?P<nivel>[^\]]+)\](?: \[pid (?P<pid>\d+)\])? (?P<mensaje>.+)'
regex_mensaje_simple = r'^(?P<mensaje>.+)$'

# vsftpd log format (ejemplo): Jan 01 12:34:56 hostname vsftpd: mensaje
ftp_regex = r'(?P<fecha>\w{3} \w{3}\s+\d{1,2} \d{2}:\d{2}:\d{2} \d{4}) \[pid (?P<pid>\d+)\](?: \[(?P<usuario>[^\]]+)\])? (?P<tipo_accion>[^:]+): Client "(?P<ip>[^"]+)"(?:, "(?P<mensaje>[^"]+)"?)?'



def parse_apache_line(line):
    print("hola mundo")
    match = re.match(apache_access_regex, line)
    if match:
        data = match.groupdict()
        fecha = datetime.strptime(data['fecha'], "%d/%b/%Y:%H:%M:%S %z")
        print("hola mundo")
        return {
            "fecha": fecha or None,
            "ip": data['ip'] or "-",
            "usuario": None if data['usuario'] == '-' else data['usuario'],
            "metodo": data['metodo'] or "-",
            "recurso": data['recurso'] or "-",
            "protocolo": data['protocolo'] or "-",
            "codigo_estado": data['codigo'] or "-",
            "tamano_respuesta": (data['tamano']) or "-",
            "user_agent": data['user_agent'] or "-"
        }
    return None

def parse_apache_error_line(line):
    # Intentamos cada regex, desde la más completa hasta la más simple
    match = re.match(regex_completo, line)
    if not match:
        match = re.match(regex_sin_fecha, line)
    if not match:
        match = re.match(regex_mensaje_simple, line)
    
    if match:
        data = match.groupdict()

        # Buscar código de mensaje tipo AH00558 si está presente
        codigo_match = re.search(r'(AH\d{5})', data.get('mensaje', ''))
        data['codigo'] = codigo_match.group(1) if codigo_match else None

        # Procesar fecha si está disponible
        raw_fecha = data.get('fecha')
        if raw_fecha:
            try:
                fecha = datetime.strptime(raw_fecha, "%a %b %d %H:%M:%S.%f %Y")
            except ValueError:
                try:
                    fecha = datetime.strptime(raw_fecha, "%a %b %d %H:%M:%S %Y")
                except ValueError:
                    fecha = datetime.now()
        else:
            fecha = None  # Línea sin timestamp

        return {
            "fecha": fecha or None,
            "nivel": data.get('nivel') or "-",
            "modulo": data.get('modulo') or "-",
            "pid_id": data.get('pid') or "-",
            "codigo_mensaje": data.get('codigo'),
            "mensaje": data.get('mensaje'),
            "origen": "Apache"
        }

    return None

def parse_ftp_line(line):
    line = line.strip()
    if not line:
        return None  # Ignorar líneas vacías

    match = re.match(ftp_regex, line)
    if match:
        data = match.groupdict()
        try:
            fecha = datetime.strptime(data['fecha'], "%a %b %d %H:%M:%S %Y")
        except ValueError:
            fecha = datetime.now()
        return {
            "fecha": fecha,
            "usuario": data.get('usuario') or "-",
            "pid_id": data.get('pid') or "-",
            "ip": data.get('ip') or "-",
            "tipo_accion": data.get('tipo_accion').strip(),
            "descripcion": data.get('mensaje') or "-"
        }
    else:
        # Solo debug si la línea no está vacía o demasiado corta
        if len(line) > 5:
            print("[DEBUG] No se pudo analizar línea FTP:", line)
    return None

def parse_log_file(file, tipo):
    if tipo == "apache":
        parser = parse_apache_line
    elif tipo == "apache_error":
        parser = parse_apache_error_line
    else:
        parser = parse_ftp_line

    parsed = []
    for line in file:
        result = parser(line)
        if result:
            parsed.append(result)
    return parsed

def filter_errors(parsed_logs):
    return [log for log in parsed_logs if
            ('codigo_estado' in log and log['codigo_estado'] >= 400) or
            ('mensaje' in log and 'error' in log['mensaje'].lower()) or
            ('descripcion' in log and 'fail' in log['descripcion'].lower())]

def generate_statistics(parsed_logs):
    stats = {
        'total': len(parsed_logs),
        'por_servicio': {},
        'por_codigo': {},
        'errores_login': 0,
        'por_host': {}
    }
    for log in parsed_logs:
        servicio = log.get('servicio', 'Desconocido')
        codigo = log.get('codigo_estado', 0)
        ip = log.get('ip', '-')

        stats['por_servicio'][servicio] = stats['por_servicio'].get(servicio, 0) + 1
        stats['por_codigo'][codigo] = stats['por_codigo'].get(codigo, 0) + 1

        if 'login incorrecto' in log.get('descripcion', '').lower():
            stats['errores_login'] += 1

        if ip != "-":
            stats['por_host'][ip] = stats['por_host'].get(ip, 0) + 1
    return stats
