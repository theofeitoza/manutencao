import random
from databases import salvar_equipamentos, salvar_funcionarios, salvar_ordens, salvar_pecas
# Funções para gerar dados de exemplo para cada tabela
def gerar_dados_pecas():
    nomes_pecas_base = [
        "Parafuso", "Engrenagem", "Sensor", "Motor", "Válvula", 
        "Placa Controladora", "Rolamento", "Cabo", "Conector", "Pistão"
    ]
    fabricantes = ["Fabricante A", "Fabricante B", "Fabricante C", "Fabricante D"]
    classes = ["Elétrico", "Mecânico", "Hidráulico", "Eletrônico"]

    dados_pecas = []
    for _ in range(20):  # Gerar 20 peças aleatórias
        nome = random.choice(nomes_pecas_base)
        descricao = f"{nome} de alta qualidade para aplicações industriais."
        fabricante = random.choice(fabricantes)
        dimensoes = f"{random.randint(10, 500)}x{random.randint(10, 500)}x{random.randint(10, 500)} mm"
        peso = round(random.uniform(0.1, 50.0), 2)
        quantidade = random.randint(1, 100)
        classe = random.choice(classes)
        dados_pecas.append((nome, descricao, fabricante, dimensoes, peso, quantidade, classe))
    return dados_pecas

def gerar_dados_funcionarios():
    nomes = ["Ana", "Bruno", "Carlos", "Diana", "Eduardo", "Fernanda", "Gabriel", "Helena", "Igor", "Juliana"]
    sobrenomes = ["Silva", "Souza", "Pereira", "Oliveira", "Costa", "Ferreira", "Almeida", "Santos"]
    funcoes = ["Técnico", "Supervisor", "Gerente"]
    equipes = ["Manutenção", "Produção", "Logística"]
    cargos = ["Operador", "Engenheiro", "Especialista"]

    dados_funcionarios = []
    for _ in range(15):  # Gerar 15 funcionários aleatórios
        nome_completo = f"{random.choice(nomes)} {random.choice(sobrenomes)}"
        documento = random.randint(10000000000, 99999999999)
        telefone = random.randint(1000000000, 9999999999)
        email = f"{nome_completo.replace(' ', '.').lower()}@empresa.com"
        funcao = random.choice(funcoes)
        equipe = random.choice(equipes)
        cargo = random.choice(cargos)
        dados_funcionarios.append((nome_completo, documento, telefone, email, funcao, equipe, cargo))
    return dados_funcionarios

def gerar_dados_ordens():
    equipamentos = ["Motor A", "Sensor B", "Válvula C", "Rolamento D", "Controlador E"]
    defeitos = ["Desgaste", "Falha elétrica", "Vazamento", "Desalinhamento", "Sobrequecimento"]
    manutencoes = ["Preventiva", "Corretiva", "Preditiva"]
    equipes = ["Equipe 1", "Equipe 2", "Equipe 3"]
    criticidades = ["Alta", "Média", "Baixa"]
    status_opcoes = ["Aberta", "Em andamento", "Concluída"]

    dados_ordens = []
    for _ in range(10):  # Gerar 10 ordens aleatórias
        equipamento = random.choice(equipamentos)
        descricao_defeito = random.choice(defeitos)
        tipo_manutencao = random.choice(manutencoes)
        equipe = random.choice(equipes)
        criticidade = random.choice(criticidades)
        status = random.choice(status_opcoes)
        dados_ordens.append((equipamento, descricao_defeito, tipo_manutencao, equipe, criticidade, status))
    return dados_ordens

def gerar_dados_equipamentos():
    nomes = ["Esteira Transportadora", "Prensa Hidráulica", "Torno Mecânico", "Fresa CNC", "Compressor de Ar"]
    locais = ["Setor A", "Setor B", "Setor C", "Setor D"]
    classes = ["Mecânico", "Elétrico", "Hidráulico"]
    criticidades = ["Alta", "Média", "Baixa"]

    dados_equipamentos = []
    for _ in range(10):  # Gerar 10 equipamentos aleatórios
        nome = random.choice(nomes)
        descricao = f"{nome} utilizado para processos industriais."
        modelo_fabricante = f"Modelo-{random.randint(100, 999)}"
        localizacao = random.choice(locais)
        custo = round(random.uniform(5000, 50000), 2)
        classe = random.choice(classes)
        criticidade = random.choice(criticidades)
        dados_equipamentos.append((nome, descricao, modelo_fabricante, localizacao, custo, classe, criticidade))
    return dados_equipamentos

# Salvar os dados no banco
# Função para salvar os dados gerados no banco de dados
def salvar_dados_gerados():
    # Salvar peças
    for peca in gerar_dados_pecas():
        salvar_pecas(*peca)
    
    # Salvar funcionários
    for funcionario in gerar_dados_funcionarios():
        salvar_funcionarios(*funcionario)
    
    # Salvar ordens
    for ordem in gerar_dados_ordens():
        salvar_ordens(*ordem)
    
    # Salvar equipamentos
    for equipamento in gerar_dados_equipamentos():
        salvar_equipamentos(*equipamento)

# Geração de dados
salvar_dados_gerados()
print("Dados gerados e salvos com sucesso!")
