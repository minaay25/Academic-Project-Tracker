import sqlite3
from werkzeug.security import generate_password_hash

connection = sqlite3.connect('database.db')

with open('schema.sql') as f:
    connection.executescript(f.read())

cur = connection.cursor()

# Örnek kullanıcının şifresini güvenli bir şekilde hash'liyoruz
hashed_pw = generate_password_hash('test1234')

cur.execute("INSERT INTO users (username, password) VALUES (?, ?)",
            ('testuser', hashed_pw)
            )

connection.commit()
connection.close()
print("Database initialized successfully with secure passwords.")