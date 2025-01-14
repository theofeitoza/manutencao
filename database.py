import sqlite3

# Caminho do banco de dados único
banco_dados_unico = "manutencao.db"

# Função para criar a tabela de usuários no banco de dados
def criar_tabela_usuarios():
    with sqlite3.connect(banco_dados_unico) as conn:
        cursor = conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE,
            senha TEXT
        )
        """)
        conn.commit()

# Função para buscar um usuário pelo email
def buscar_usuario(email):
    with sqlite3.connect(banco_dados_unico) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, email, senha FROM usuarios WHERE email = ?", (email,))
        usuario = cursor.fetchone()
    return usuario

# Função para cadastrar um novo usuário
def cadastrar_usuario(email, senha):
    try:
        with sqlite3.connect(banco_dados_unico) as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO usuarios (email, senha) VALUES (?, ?)", (email, senha))
            conn.commit()
        return True
    except sqlite3.IntegrityError:
        # Caso o email já exista no banco
        return False
