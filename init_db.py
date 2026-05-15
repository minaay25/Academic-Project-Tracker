import sqlite3

def init_db():
    connection = sqlite3.connect('database.db')
    
    with open('schema.sql') as f:
        connection.executescript(f.read())

    # Add a sample user for testing (Password is plaintext for now, will be hashed later)
    cur = connection.cursor()
    cur.execute("INSERT INTO users (username, password) VALUES (?, ?)", ('testuser', '123456'))

    connection.commit()
    connection.close()
    print("Database initialized successfully!")

if __name__ == '__main__':
    init_db()