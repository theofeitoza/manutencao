import sqlite3
from datetime import datetime, timedelta

BANCO_DADOS_UNICO = "manutencao.db"

def obter_conexao():
    return sqlite3.connect(BANCO_DADOS_UNICO)

def executar_query(query, parametros=(), return_type='all'):
    with sqlite3.connect(BANCO_DADOS_UNICO) as conexao:
        cursor = conexao.cursor()
        cursor.execute(query, parametros)
        
        if query.strip().upper().startswith("INSERT"):
            conexao.commit()
            return cursor.lastrowid
        elif return_type == 'all':
            return cursor.fetchall()
        elif return_type == 'one':
            return cursor.fetchone()
        else:
            conexao.commit()
            return None

def ler_colunas_tabela(tabela):
    if tabela == "funcionarios":
        return ["id", "nome_completo", "documento", "telefone", "email", "funcao", "nome_equipe", "cargo"]
    elif tabela == "ordens":
        return ["Id", "Equipamento", "Descricao_defeito", "Custo", "Equipe", 
                "Classificacao", "Criticidade", "Status", "Data_criacao", "Data_inicio_execucao", "Data_fim_execucao",
                "Horario_abertura", "Horario_fechamento"]
    elif tabela == "pecas":
        return ["Id", "Nome_peca", "Descricao", "Fabricante", "Dimensoes", "Peso", "Quantidade", "Classe", "Custo_Unitario"]
    else:
        with sqlite3.connect(BANCO_DADOS_UNICO) as conexao:
            cursor = conexao.cursor()
            cursor.execute(f"PRAGMA table_info({tabela})")
            return [linha[1] for linha in cursor.fetchall()]

def ler_dados_filtrados(tabela, colunas, coluna_ordem="id", direcao="ASC", filtro=""):
    if tabela == "funcionarios":
        query_base = "SELECT f.id, f.nome_completo, f.documento, f.telefone, f.email, f.funcao, e.nome_equipe, f.cargo FROM funcionarios f LEFT JOIN equipes e ON f.equipe_id = e.id"
        colunas_para_filtro = ["f.nome_completo", "f.documento", "f.telefone", "f.email", "f.funcao", "e.nome_equipe", "f.cargo"]
    elif tabela == "ordens": 
        query_base = "SELECT Id, Equipamento, Descricao_defeito, Custo, Equipe, Classificacao, Criticidade, Status, Data_criacao, Data_inicio_execucao, Data_fim_execucao, Horario_abertura, Horario_fechamento FROM ordens"
        colunas_para_filtro = ["Equipamento", "Descricao_defeito", "Custo", "Equipe", "Classificacao", "Criticidade", "Status", "Data_criacao", "Data_inicio_execucao", "Data_fim_execucao"]
    
    elif tabela == "pecas":
        query_base = "SELECT Id, Nome_peca, Descricao, Fabricante, Dimensoes, Peso, Quantidade, Classe, Custo_Unitario FROM pecas"
        colunas_para_filtro = ["Nome_peca", "Descricao", "Fabricante", "Classe"]
    
    else:
        query_base = f"SELECT * FROM {tabela}"
        colunas_para_filtro = colunas 

    filtro_query = " WHERE " + " OR ".join([f"{col} LIKE ?" for col in colunas_para_filtro]) if filtro else ""
    parametros = tuple(f"%{filtro}%" for _ in colunas_para_filtro) if filtro else ()
    
    if tabela == "funcionarios" and coluna_ordem == "nome_equipe":
        coluna_ordem_real = "e.nome_equipe"
    elif tabela == "funcionarios":
        coluna_ordem_real = f"f.{coluna_ordem}"
    else:
        coluna_ordem_real = coluna_ordem

    query = f"{query_base}{filtro_query} ORDER BY {coluna_ordem_real} {direcao}"
    return executar_query(query, parametros)

def _get_date_range_sql(period: str):
    end_date_sql = "DATE('now')"
    if period == "last_week":
        start_date_sql = "DATE('now', '-7 days')"
    elif period == "last_month":
        start_date_sql = "DATE('now', '-1 month')"
    elif period == "last_6_months":
        start_date_sql = "DATE('now', '-6 months')"
    else: 
        start_date_sql = "DATE('now', '-12 months')"
    
    return f"DATE(Data_criacao) BETWEEN {start_date_sql} AND {end_date_sql}"

def buscar_top_equipamentos_com_ordens(limit=5, period="last_12_months"):
    date_range_sql = _get_date_range_sql(period)
    query = f"""
        SELECT 
            Equipamento, 
            COUNT(Id) as TotalOrdens
        FROM ordens
        WHERE {date_range_sql}
        GROUP BY Equipamento
        ORDER BY TotalOrdens DESC
        LIMIT ?
    """
    return executar_query(query, (limit,))

def buscar_ordens_por_equipe(limit=5, period="last_12_months"):
    date_range_sql = _get_date_range_sql(period)
    query = f"""
        SELECT 
            Equipe, 
            COUNT(Id) as TotalOrdens
        FROM ordens
        WHERE {date_range_sql}
        AND Equipe IS NOT NULL
        GROUP BY Equipe
        ORDER BY TotalOrdens DESC
        LIMIT ?
    """
    return executar_query(query, (limit,))

def buscar_ordens_por_classificacao(period="last_12_months"):
    date_range_sql = _get_date_range_sql(period)
    query = f"""
        SELECT 
            Classificacao, 
            COUNT(Id) as TotalOrdens
        FROM ordens
        WHERE {date_range_sql}
        AND Classificacao IS NOT NULL
        GROUP BY Classificacao
        ORDER BY TotalOrdens DESC
    """
    return executar_query(query)

def buscar_custo_por_classificacao(period="last_12_months"):
    date_range_sql = _get_date_range_sql(period)
    query = f"""
        SELECT 
            Classificacao, 
            SUM(Custo) as CustoTotal
        FROM ordens
        WHERE {date_range_sql}
        AND Classificacao IS NOT NULL
        AND Custo IS NOT NULL
        GROUP BY Classificacao
        ORDER BY CustoTotal DESC
    """
    return executar_query(query)

def buscar_custo_por_data(period="last_12_months"):
    end_date = datetime.now().date()
    
    if period == "last_week":
        start_date = end_date - timedelta(days=6)
        group_by_format = "%Y-%m-%d"
    elif period == "last_month":
        start_date = end_date - timedelta(days=29)
        group_by_format = "%Y-%m-%d"
    elif period == "last_6_months":
        start_date = end_date - timedelta(days=180)
        group_by_format = "%Y-%m"
    else:
        start_date = end_date - timedelta(days=365)
        group_by_format = "%Y-%m"
    
    group_by_column = f"STRFTIME('{group_by_format}', Data_criacao)"

    query = f"""
        SELECT 
            {group_by_column} as DataAgrupada, 
            SUM(Custo) as CustoTotal
        FROM ordens
        WHERE DATE(Data_criacao) BETWEEN DATE(?) AND DATE(?)
        AND Custo IS NOT NULL
        GROUP BY DataAgrupada
        ORDER BY DataAgrupada ASC
    """
    return executar_query(query, (start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")))

def buscar_horas_manutencao_total(period: str): 
    date_range_sql = _get_date_range_sql(period) 
    query = f"""
        SELECT Horario_abertura, Horario_fechamento
        FROM ordens
        WHERE Status = 'Encerrada'
        AND Horario_abertura IS NOT NULL
        AND Horario_fechamento IS NOT NULL
        AND {date_range_sql} -- Filtra pelo período de criação
    """
    return executar_query(query)