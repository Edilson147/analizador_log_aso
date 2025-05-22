# Analizador de Logs en Flask con MySQL

Este proyecto es una aplicación web desarrollada con Flask que permite analizar archivos de logs de los servicios Apache y FTP, almacenarlos en una base de datos MySQL y realizar operaciones de búsqueda, filtrado, alerta y generación de reportes estadísticos.

## Requisitos

* Python 3.x
* Flask
* MySQL o MariaDB
* Sistema operativo: openSUSE Leap 15.6 (funciona en cualquier Linux)

## Instalación

### 1. Instalar dependencias del sistema

```bash
sudo zypper install python3 python3-pip python3-devel mariadb libmysqlclient-devel
```

### 2. Instalar dependencias de Python

```bash
pip install flask flask-mysqldb
```

### 3. Crear base de datos en MySQL/MariaDB

```sql
CREATE DATABASE logdb CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'loguser'@'localhost' IDENTIFIED BY 'tu_password';
GRANT ALL PRIVILEGES ON logdb.* TO 'loguser'@'localhost';
FLUSH PRIVILEGES;
```

### 4. Configurar archivo `config.py`

```python
# config.py
MYSQL_HOST = 'localhost'
MYSQL_USER = 'loguser'
MYSQL_PASSWORD = 'tu_password'
MYSQL_DB = 'logdb'
```

## Estructura del Proyecto

```
log_analyzer/
├── app
│   ├── __init__.py
│   ├── log_parser.py
│   ├── models.py
│   ├── __pycache__
│   │   ├── __init__.cpython-36.pyc
│   │   ├── log_parser.cpython-36.pyc
│   │   ├── models.cpython-36.pyc
│   │   └── routes.cpython-36.pyc
│   ├── routes.py
│   ├── static
│   │   └── styles.css
│   └── templates
│       ├── base.html
│       ├── index.html
│       ├── logs.html
│       ├── reportes_apache.html
│       ├── reportes_ftp.html
│       └── ver_logs.html
├── config.py
├── __pycache__
│   └── config.cpython-36.pyc
├── README.md
├── requirements.txt
├── run.py
└── static
    └── uploads
```

## Ejecución

```bash
python run.py
```

Abre tu navegador en:

```
http://localhost:5000/
```

## Características Principales

* Soporte para logs de Apache y FTP
* Análisis de logs y almacenamiento en base de datos
* Búsqueda simple y avanzada (por texto, rango de fechas, AND/OR)
* Detección de errores y alertas
* Reportes estadísticos: cantidad por servicio, código, errores de login, peticiones por host
* Interfaz web simple para carga y visualización



