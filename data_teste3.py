import sqlite3

# Caminho do banco de dados 
banco_dados_unico = "manutencao.db"

def buscar_nomes_pecas():
    try:
        # Conecte ao banco de dados
        conn = sqlite3.connect(banco_dados_unico)  # Substitua pelo caminho correto do seu banco
        cursor = conn.cursor()

        # Execute a consulta para buscar os nomes das peças
        cursor.execute("SELECT DISTINCT nome_peca FROM pecas")  # Ajuste o nome da tabela/coluna conforme necessário
        nomes = [row[0] for row in cursor.fetchall()]  # Extrai os nomes da consulta
        
        conn.close()
        return nomes

    except Exception as e:
        print(f"Erro ao buscar nomes das peças: {e}")
        return []

def atualizar_peca(nome_peca, descricao, fabricante, dimensoes, peso, quantidade, classe):
    with sqlite3.connect(banco_dados_unico) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE pecas
            SET descricao = ?, fabricante = ?, dimensoes = ?, peso = ?, quantidade = ?, classe = ?
            WHERE nome_peca = ?
            """,
            (descricao, fabricante, dimensoes, peso, quantidade, classe, nome_peca),
        )
        conn.commit()

def buscar_dados_peca(nome_peca):
    # Estabeleça uma conexão com o banco de dados
    conn = sqlite3.connect(banco_dados_unico)  # Substitua pelo seu banco de dados
    cursor = conn.cursor()

    # Consulta SQL para pegar os dados da peça
    cursor.execute("SELECT descricao, fabricante, dimensoes, peso, quantidade, classe FROM pecas WHERE nome_peca = ?", (nome_peca,))
    
    # Buscar o resultado
    dados_peca = cursor.fetchone()  # Pega a primeira linha encontrada (se houver)

    # Fechar a conexão com o banco
    conn.close()

    # Se encontrar a peça, retornar os dados, senão, retorna None
    if dados_peca:
        return {
            "descricao": dados_peca[0],
            "fabricante": dados_peca[1],
            "dimensoes": dados_peca[2],
            "peso": dados_peca[3],
            "quantidade": dados_peca[4],
            "classe": dados_peca[5]
        }
    else:
        return None

# Função genérica para executar queries
def executar_query(db_name, query, params=None, fetchall=True):
    with sqlite3.connect(db_name) as conn:
        cursor = conn.cursor()
        cursor.execute(query, params or [])
        print(f"Query: {query}")
        print(f"Parâmetros: {params}")
        if fetchall:
            return cursor.fetchall()
        conn.commit()

# Funções para criar as tabelas no banco único
def criar_tabela_pecas():
    query = """
        CREATE TABLE IF NOT EXISTS pecas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome_peca TEXT,
            descricao TEXT,
            fabricante TEXT,
            dimensoes TEXT,
            peso FLOAT,
            quantidade INT,
            classe TEXT
        )
    """
    executar_query(banco_dados_unico, query, fetchall=False)

def criar_tabela_equipamentos():
    query = """
        CREATE TABLE IF NOT EXISTS equipamentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT,
            descricao TEXT,
            modelo_fabricante TEXT,
            localizacao TEXT,
            custo FLOAT,
            classe TEXT,
            criticidade TEXT
        )
    """
    executar_query(banco_dados_unico, query, fetchall=False)

def criar_tabela_ordens():
    query = """
        CREATE TABLE IF NOT EXISTS ordens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            equipamento TEXT,
            descricao_defeito TEXT,
            tipo_manutencao TEXT,
            equipe TEXT,
            criticidade TEXT,
            status TEXT,
            data TEXT  -- Adicionada coluna para armazenar a data
        )
    """
    executar_query(banco_dados_unico, query, fetchall=False)

def criar_tabela_funcionarios():
    query = """
        CREATE TABLE IF NOT EXISTS funcionarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome_completo TEXT,
            documento INT,
            telefone INT,
            email TEXT,
            funcao TEXT,
            equipe TEXT,
            cargo TEXT
        )
    """
    executar_query(banco_dados_unico, query, fetchall=False)

# Funções para salvar os dados nas tabelas
def salvar_pecas(nome_peca, descricao, fabricante, dimensoes, peso, quantidade, classe):
    query = """
        INSERT INTO pecas (nome_peca, descricao, fabricante, dimensoes, peso, quantidade, classe)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """
    executar_query(banco_dados_unico, query, (nome_peca, descricao, fabricante, dimensoes, peso, quantidade, classe), fetchall=False)

def salvar_equipamentos(nome, descricao, modelo_fabricante, localizacao, custo, classe, criticidade):
    query = """
        INSERT INTO equipamentos (nome, descricao, modelo_fabricante, localizacao, custo, classe, criticidade)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """
    executar_query(banco_dados_unico, query, (nome, descricao, modelo_fabricante, localizacao, custo, classe, criticidade), fetchall=False)

def salvar_ordens(equipamento, descricao_defeito, tipo_manutencao, equipe, criticidade, status, data):
    query = """
        INSERT INTO ordens (equipamento, descricao_defeito, tipo_manutencao, equipe, criticidade, status, data)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """
    executar_query(banco_dados_unico, query, (equipamento, descricao_defeito, tipo_manutencao, equipe, criticidade, status, data), fetchall=False)

def salvar_funcionarios(nome_completo, documento, telefone, email, funcao, equipe, cargo):
    query = """
        INSERT INTO funcionarios (nome_completo, documento, telefone, email, funcao, equipe, cargo)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """
    executar_query(banco_dados_unico, query, (nome_completo, documento, telefone, email, funcao, equipe, cargo), fetchall=False)

# Criar todas as tabelas
criar_tabela_pecas()
criar_tabela_equipamentos()
criar_tabela_ordens()
criar_tabela_funcionarios()

print("Banco de dados criado com sucesso!")
