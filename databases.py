import sqlite3
from datetime import datetime
from db_utils import executar_query

banco_dados_unico = "manutencao.db"
USUARIO_LOGADO_ID = None

def set_usuario_logado_id(user_id):
    global USUARIO_LOGADO_ID
    USUARIO_LOGADO_ID = user_id

def get_usuario_logado_id():
    return USUARIO_LOGADO_ID

def criar_tabela_usuarios():
    query = """
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE,
            senha TEXT
        )
    """
    executar_query(query, return_type=None)

def buscar_usuario(email):
    with sqlite3.connect(banco_dados_unico) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, email, senha FROM usuarios WHERE email = ?", (email,))
        return cursor.fetchone()

def cadastrar_usuario(email, senha):
    try:
        query = "INSERT INTO usuarios (email, senha) VALUES (?, ?)"
        executar_query(query, (email, senha), return_type=None)
        return True
    except sqlite3.IntegrityError:
        return False

def criar_tabela_pecas():
    query = """
        CREATE TABLE IF NOT EXISTS pecas (
            Id INTEGER PRIMARY KEY AUTOINCREMENT,
            Nome_peca TEXT, 
            Descricao TEXT, 
            Fabricante TEXT, 
            Dimensoes TEXT,
            Peso FLOAT, 
            Quantidade INT, 
            Classe TEXT,
            Custo_Unitario REAL DEFAULT 0.0
        )
    """
    executar_query(query, return_type=None)

def salvar_pecas(nome_peca, descricao, fabricante, dimensoes, peso, quantidade, classe, custo_unitario):
    query = """
        INSERT INTO pecas (Nome_peca, Descricao, Fabricante, Dimensoes, Peso, Quantidade, Classe, Custo_Unitario)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """
    executar_query(query, (nome_peca, descricao, fabricante, dimensoes, peso, quantidade, classe, custo_unitario), return_type=None)

def atualizar_peca(id_peca, nome_peca, descricao, fabricante, dimensoes, peso, quantidade, classe, custo_unitario):
    query = """
            UPDATE pecas
            SET Nome_peca = ?, Descricao = ?, Fabricante = ?, Dimensoes = ?, Peso = ?, 
                Quantidade = ?, Classe = ?, Custo_Unitario = ?
            WHERE Id = ?
            """
    executar_query(query, (nome_peca, descricao, fabricante, dimensoes, peso, quantidade, classe, custo_unitario, id_peca), return_type=None)

def buscar_dados_peca(nome_peca):
    query = "SELECT Id, Nome_peca, Descricao, Fabricante, Dimensoes, Peso, Quantidade, Classe, Custo_Unitario FROM pecas WHERE Nome_peca = ?"
    dados_peca = executar_query(query, (nome_peca,), return_type='one')
    if dados_peca:
        return {
            "Id": dados_peca[0], "Nome_peca": dados_peca[1], "Descricao": dados_peca[2],
            "Fabricante": dados_peca[3], "Dimensoes": dados_peca[4], "Peso": dados_peca[5],
            "Quantidade": dados_peca[6], "Classe": dados_peca[7], "Custo_Unitario": dados_peca[8]
        }
    else:
        return None
        
def buscar_nomes_pecas():
    try:
        query = "SELECT DISTINCT nome_peca FROM pecas"
        nomes = [row[0] for row in executar_query(query)] 
        return nomes
    except Exception as e:
        print(f"Erro ao buscar nomes das peças: {e}")
        return []

def criar_tabela_equipamentos():
    query = """
        CREATE TABLE IF NOT EXISTS equipamentos (
            Id INTEGER PRIMARY KEY AUTOINCREMENT,
            Nome TEXT, Descricao TEXT, Modelo_fabricante TEXT, Localizacao TEXT,
            Custo FLOAT, Classe TEXT, Criticidade TEXT
        )
    """
    executar_query(query, return_type=None)

def criar_tabela_ordens():
    query_create = """
        CREATE TABLE IF NOT EXISTS ordens (
            Id INTEGER PRIMARY KEY AUTOINCREMENT,
            Equipamento TEXT, Descricao_defeito TEXT,
            Custo REAL DEFAULT 0.0,
            Equipe TEXT, Classificacao TEXT, Criticidade TEXT, Status TEXT,
            Data_criacao TEXT DEFAULT CURRENT_TIMESTAMP,
            Data_inicio_execucao TEXT, Data_fim_execucao TEXT,
            Horario_abertura TEXT, Horario_fechamento TEXT
        )
    """
    executar_query(query_create, return_type=None)

def criar_tabela_ordem_pecas():
    query = """
        CREATE TABLE IF NOT EXISTS ordem_pecas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ordem_id INTEGER NOT NULL,
            peca_id INTEGER NOT NULL,
            quantidade_utilizada INTEGER NOT NULL,
            FOREIGN KEY (ordem_id) REFERENCES ordens(Id),
            FOREIGN KEY (peca_id) REFERENCES pecas(Id)
        )
    """
    executar_query(query, return_type=None)

def criar_tabela_equipes():
    query = """
        CREATE TABLE IF NOT EXISTS equipes (
            Id INTEGER PRIMARY KEY AUTOINCREMENT,
            Nome_equipe TEXT UNIQUE
        )
    """
    executar_query(query, return_type=None)

def criar_tabela_funcionarios():
    query = """
        CREATE TABLE IF NOT EXISTS funcionarios (
            Id INTEGER PRIMARY KEY AUTOINCREMENT,
            Nome_completo TEXT, Documento INT, Telefone INT, Email TEXT,
            Funcao TEXT, Equipe_id INTEGER, Cargo TEXT,
            FOREIGN KEY (Equipe_id) REFERENCES equipes(Id)
        )
    """
    executar_query(query, return_type=None)

def criar_tabela_logs():
    query = """
        CREATE TABLE IF NOT EXISTS logs (
            Id INTEGER PRIMARY KEY AUTOINCREMENT,
            Id_ordem INTEGER, Tipo_alteracao TEXT, Detalhes_alteracao TEXT,
            Data_alteracao TEXT DEFAULT CURRENT_TIMESTAMP, Usuario_id INTEGER,
            FOREIGN KEY (Usuario_id) REFERENCES usuarios(Id)
        )
    """
    executar_query(query, return_type=None)

def salvar_equipamentos(nome, descricao, modelo_fabricante, localizacao, custo, classe, criticidade):
    query = """
        INSERT INTO equipamentos (Nome, Descricao, Modelo_fabricante, Localizacao, Custo, Classe, Criticidade)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """
    executar_query(query, (nome, descricao, modelo_fabricante, localizacao, custo, classe, criticidade), return_type=None)

def atualizar_equipamento(id_equipamento, nome, descricao, modelo_fabricante, localizacao, custo, classe, criticidade):
    query = """
        UPDATE equipamentos
        SET Nome = ?, Descricao = ?, Modelo_fabricante = ?, Localizacao = ?, Custo = ?, Classe = ?, Criticidade = ?
        WHERE Id = ?
    """
    executar_query(query, (nome, descricao, modelo_fabricante, localizacao, custo, classe, criticidade, id_equipamento), return_type=None)

def salvar_ordens(equipamento, descricao_defeito, equipe, classificacao, criticidade, status, data_inicio, data_fim):
    query = """
        INSERT INTO ordens (Equipamento, Descricao_defeito, Equipe, Classificacao, Criticidade, Status, Data_inicio_execucao, Data_fim_execucao)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """
    return executar_query(query, (equipamento, descricao_defeito, equipe, classificacao, criticidade, status, data_inicio, data_fim), return_type='lastrowid')

def recalcular_custo_ordem(ordem_id: int):
    query_calculo = """
        SELECT SUM(p.Custo_Unitario * op.quantidade_utilizada)
        FROM ordem_pecas op
        JOIN pecas p ON op.peca_id = p.Id
        WHERE op.ordem_id = ?
    """
    resultado = executar_query(query_calculo, (ordem_id,), return_type='one')
    novo_custo = resultado[0] if resultado and resultado[0] is not None else 0.0

    query_update = "UPDATE ordens SET Custo = ? WHERE Id = ?"
    executar_query(query_update, (novo_custo, ordem_id), return_type=None)
    print(f"Custo da ordem {ordem_id} atualizado para {novo_custo}")

def associar_peca_a_ordem(ordem_id: int, peca_id: int, quantidade: int):
    with sqlite3.connect(banco_dados_unico) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO ordem_pecas (ordem_id, peca_id, quantidade_utilizada) VALUES (?, ?, ?)",
            (ordem_id, peca_id, quantidade)
        )
        cursor.execute(
            "UPDATE pecas SET Quantidade = Quantidade - ? WHERE Id = ?",
            (quantidade, peca_id)
        )
        conn.commit()
    recalcular_custo_ordem(ordem_id)

def registrar_abertura_ordem(ordem_id: int, horario_abertura: datetime):
    query_select = "SELECT Horario_abertura FROM ordens WHERE Id = ?"
    resultado = executar_query(query_select, (ordem_id,), return_type='one')
    if resultado and (resultado[0] is None or resultado[0] == ''):
        horario_str = horario_abertura.strftime('%Y-%m-%d %H:%M:%S')
        query_update = "UPDATE ordens SET Horario_abertura = ? WHERE Id = ?"
        executar_query(query_update, (horario_str, ordem_id), return_type=None)
        print(f"Ordem {ordem_id} aberta pela primeira vez às {horario_str}")
    else:
        print(f"Ordem {ordem_id} já havia sido aberta. Nenhuma alteração no horário de abertura.")

def registrar_fechamento_ordem(ordem_id: int, horario_fechamento: datetime):
    horario_str = horario_fechamento.strftime('%Y-%m-%d %H:%M:%S')
    query = "UPDATE ordens SET Horario_fechamento = ?, Status = 'Encerrada' WHERE Id = ?"
    executar_query(query, (horario_str, ordem_id), return_type=None)
    print(f"Ordem {ordem_id} encerrada às {horario_str}")

def salvar_funcionarios(nome_completo, documento, telefone, email, funcao, equipe_id, cargo):
    query = """
        INSERT INTO funcionarios (Nome_completo, Documento, Telefone, Email, Funcao, Equipe_id, Cargo)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """
    executar_query(query, (nome_completo, documento, telefone, email, funcao, equipe_id, cargo), return_type=None)

def atualizar_funcionario(id_funcionario, nome_completo, documento, telefone, email, funcao, equipe_id, cargo):
    query = """
        UPDATE funcionarios
        SET Nome_completo = ?, Documento = ?, Telefone = ?, Email = ?, Funcao = ?, Equipe_id = ?, Cargo = ?
        WHERE Id = ?
    """
    executar_query(query, (nome_completo, documento, telefone, email, funcao, equipe_id, cargo, id_funcionario), return_type=None)

def salvar_equipe(nome_equipe):
    query = "INSERT INTO equipes (Nome_equipe) VALUES (?)"
    return executar_query(query, (nome_equipe,), return_type='lastrowid')

def buscar_equipes():
    query = "SELECT id, Nome_equipe FROM equipes"
    return executar_query(query)

def registrar_log(id_ordem, tipo_alteracao, detalhes_alteracao, usuario_id=None):
    query = """
        INSERT INTO logs (Id_ordem, Tipo_alteracao, Detalhes_alteracao, Usuario_id)
        VALUES (?, ?, ?, ?)
    """
    executar_query(query, (id_ordem, tipo_alteracao, detalhes_alteracao, usuario_id), return_type=None)

def buscar_pecas_para_dropdown():
    query = "SELECT Id, Nome_peca, Quantidade FROM pecas WHERE Quantidade > 0 ORDER BY Nome_peca"
    return executar_query(query)

def buscar_pecas_por_ordem(ordem_id: int):
    query = """
        SELECT p.Nome_peca, op.quantidade_utilizada
        FROM ordem_pecas op
        JOIN pecas p ON op.peca_id = p.Id
        WHERE op.ordem_id = ?
    """
    return executar_query(query, (ordem_id,))

def inicializar_banco():
    criar_tabela_usuarios()
    criar_tabela_pecas()
    criar_tabela_equipamentos()
    criar_tabela_ordens()
    criar_tabela_equipes()
    criar_tabela_funcionarios()
    criar_tabela_logs()
    criar_tabela_ordem_pecas()
    print("Banco de dados verificado/inicializado com sucesso!")

inicializar_banco()