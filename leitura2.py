import sqlite3

def ler_ordens():
    # Conectando ao banco de dados SQLite
    conexao = sqlite3.connect("ordens.db")
    cursor = conexao.cursor()
    
    # Realizando a consulta para selecionar todas as ordens
    cursor.execute("SELECT id, equipamento, descricao_defeito, tipo_manutencao, equipe, criticidade FROM ordens")

    # Obtendo todos os resultados da consulta
    ordens = cursor.fetchall()

    # Fechando a conexão com o banco de dados
    conexao.close()

    # Exibindo os resultados
    for ordem in ordens:
        print(f"ID: {ordem[0]}")
        print(f"Equipamento: {ordem[1]}")
        print(f"Descrição: {ordem[2]}")
        print(f"Tipo de Manutenção: {ordem[3]}")
        print(f"Equipe: {ordem[4]}")
        print(f"Classificação: {ordem[5]}")
        print("-" * 40)

# Chama a função para ler e exibir as ordens
ler_ordens()
