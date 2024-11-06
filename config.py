import mysql.connector

# Fonction de connexion à la base de données
def connect_to_database():
    db = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="facial_recognition"
    )
    cursor = db.cursor()
    return db, cursor

# Fonction pour fermer la connexion à la base de données
def close_database_connection(db, cursor):
    cursor.close()
    db.close()
