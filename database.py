from flask_mysqldb import MySQL

mysql = MySQL()

def init_db(app):
    app.config.from_pyfile('config.py')
    mysql.init_app(app)
