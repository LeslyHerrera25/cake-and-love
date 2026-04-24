import pymysql

# 1. Engañamos a Django para que use PyMySQL como si fuera mysqlclient
pymysql.install_as_MySQLdb()

# 2. Engañamos a Django sobre la versión para que no nos bloquee
pymysql.version_info = (2, 2, 1, "final", 0)