import sqlite3

# Função para conectar e ler os dados da tabela
def ler_dados():
    # Conectar ao banco de dados
    conexao = sqlite3.connect("equipamentos.db")
    cursor = conexao.cursor()

    # Executar a consulta SQL para ler todos os registros
    cursor.execute("SELECT * FROM equipamentos")
    dados = cursor.fetchall()

    # Fechar a conexão
    conexao.close()

    # Exibir os dados lidos
    if dados:
        for registro in dados:
            print(f"ID: {registro[0]}")
            print(f"Nome: {registro[1]}")
            print(f"Descrição: {registro[2]}")
            print(f"Modelo/Fabricante: {registro[3]}")
            print(f"Localização: {registro[4]}")
            print(f"Custo: {registro[5]}")
            print(f"Classe: {registro[6]}")
            print(f"Criticidade: {registro[7]}")
            
            print("-" * 40)
    else:
        print("Nenhum dado encontrado na tabela.")

# Chamar a função para ler os dados
ler_dados()
