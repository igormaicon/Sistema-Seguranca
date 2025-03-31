import sqlite3

DATABASE = 'instance/sistema_seguranca.db'

def get_db():
    db = sqlite3.connect(DATABASE)
    db.row_factory = sqlite3.Row  # Isso permite acessar as colunas por nome
    return db

def init_db():
    with get_db() as db:
        with open('schema.sql', 'r') as f:
            db.cursor().executescript(f.read())
        db.commit()

if __name__ == '__main__':
    init_db()
    print("Banco de dados inicializado com sucesso!")