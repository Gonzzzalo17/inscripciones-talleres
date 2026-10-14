import pymysql

pymysql.version_info = (2, 2, 8, "final", 0)
pymysql.install_as_MySQLdb()

# Desactivar la verificación de versión de MySQL en Django
from django.db.backends.mysql.base import DatabaseWrapper

DatabaseWrapper.check_database_version_supported = lambda self: None