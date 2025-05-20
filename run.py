# run.py
from flask import Flask
from flask_mysqldb import MySQL
from app.routes import bp
from app.models import init_db
import config

app = Flask(__name__, template_folder='app/templates')
app.config.from_object(config)

app.mysql = MySQL(app)

with app.app_context():
    init_db(app.mysql)

app.register_blueprint(bp)

if __name__ == '__main__':
    app.run(debug=True)

