import flet as ft
from databases import salvar_ordens  # Ajuste o import conforme necessário
import sqlite3

# Caminho do banco de dados único
BANCO_DADOS_UNICO = "manutencao.db"

# Função para conectar e buscar os dados de equipamentos no banco
def buscar_equipamentos():
    conexao = sqlite3.connect(BANCO_DADOS_UNICO)  # Conectar ao banco de dados único
    cursor = conexao.cursor()
    cursor.execute("SELECT id, nome FROM equipamentos")  # Busca ID e nome dos equipamentos
    equipamentos = cursor.fetchall()  # Retorna todos os registros
    conexao.close()
    return equipamentos  # Lista de tuplas (id, nome)

# Função para exibir o equipamento selecionado
def exibir_equipamento_selecionado(equipamento_id):
    conexao = sqlite3.connect(BANCO_DADOS_UNICO)  # Conectar ao banco de dados único
    cursor = conexao.cursor()
    cursor.execute("SELECT * FROM equipamentos WHERE id=?", (equipamento_id,))  # Busca o equipamento pelo ID
    equipamento = cursor.fetchone()  # Retorna um único registro
    conexao.close()
    return equipamento  # Tupla com os dados do equipamento

def criar_dialogo_ordens(page: ft.Page, atualizar_tabela_callback):
    page.theme_mode = ft.ThemeMode.LIGHT 

    # Referências para os campos
    dropdown_ref = ft.Ref[ft.Dropdown]()
    descricao_defeito_ref = ft.Ref[ft.TextField]()
    tipo_manutencao_ref = ft.Ref[ft.TextField]()
    equipe_ref = ft.Ref[ft.RadioGroup]()
    classificacao_ref = ft.Ref[ft.RadioGroup]()
    status_ref = ft.Ref[ft.RadioGroup]()
    equipe_erro_ref = ft.Ref[ft.Text]()
    classificacao_erro_ref = ft.Ref[ft.Text]()
    status_erro_ref = ft.Ref[ft.Text]()
    cadastro_dialog_ref = ft.Ref[ft.AlertDialog]()

    def cadastrar_ordem(e):
        # Obter os valores dos campos
        equipamento = dropdown_ref.current.value
        descricao_defeito = descricao_defeito_ref.current.value.strip()
        tipo_manutencao = tipo_manutencao_ref.current.value.strip()
        equipe = equipe_ref.current.value
        classificacao = classificacao_ref.current.value
        status = status_ref.current.value
        campos_invalidos = False

        # Validação dos campos de texto
        if not descricao_defeito:
            descricao_defeito_ref.current.error_text = "Preenchimento obrigatório"
            campos_invalidos = True
        else:
            descricao_defeito_ref.current.error_text = None

        if not tipo_manutencao:
            tipo_manutencao_ref.current.error_text = "Preenchimento obrigatório"
            campos_invalidos = True
        else:
            tipo_manutencao_ref.current.error_text = None

        # Validação dos RadioGroups
        if not equipe:
            equipe_erro_ref.current.value = "Selecione uma equipe"
            campos_invalidos = True
        else:
            equipe_erro_ref.current.value = None

        if not classificacao:
            classificacao_erro_ref.current.value = "Selecione uma classificação"
            campos_invalidos = True
        else:
            classificacao_erro_ref.current.value = None

        if not status:
            status_erro_ref.current.value = "Selecione um status"
            campos_invalidos = True
        else:
            status_erro_ref.current.value = None

        page.update()

        if campos_invalidos:
            return

        # Salvar a ordem de serviço no banco de dados
        id_gerado = salvar_ordens(equipamento, descricao_defeito, tipo_manutencao, equipe, classificacao, status)

        atualizar_tabela_callback()

        # Exibir uma mensagem de sucesso
        fechar_dialogo(None)
        page.snack_bar = ft.SnackBar(ft.Text(f"Ordem de serviço gerada com sucesso! ID: {id_gerado}"))
        page.snack_bar.open = True
        page.update()
        limpar_campos(None)

    def limpar_campos(e):
        dropdown_ref.current.value = None
        descricao_defeito_ref.current.value = ""
        tipo_manutencao_ref.current.value = ""
        equipe_ref.current.value = None
        classificacao_ref.current.value = None
        status_ref.current.value = None
        descricao_defeito_ref.current.error_text = None
        tipo_manutencao_ref.current.error_text = None
        equipe_erro_ref.current.value = None
        classificacao_erro_ref.current.value = None
        status_erro_ref.current.value = None
        page.update()

    def fechar_dialogo(e):
        cadastro_dialog_ref.current.open = False
        page.update()

    cadastro_dialog = ft.AlertDialog(
        modal=True,
        content=ft.Column(
            [
                ft.Text("Nova Ordem de Serviço", size=50, color=ft.colors.BLACK, weight=ft.FontWeight.BOLD),
                ft.Dropdown(
                    ref=dropdown_ref,
                    label="Selecione um Equipamento",
                    options=[
                        ft.dropdown.Option(f"{equipamento[1]} (ID: {equipamento[0]})")
                        for equipamento in buscar_equipamentos()
                    ],
                ),
                ft.TextField(
                    adaptive=True,
                    label="Descrição do defeito",
                    max_length=400,
                    multiline=True,
                    ref=descricao_defeito_ref
                ),
                ft.TextField(
                    adaptive=True,
                    label="Tipo de manutenção",
                    max_length=50,
                    ref=tipo_manutencao_ref
                ),
                ft.Row([ 
                    ft.RadioGroup(
                        ref=equipe_ref,
                        content=ft.Column([ 
                            ft.Text("Equipe"),
                            ft.Radio(value="Elétrica", label="Elétrica"),
                            ft.Radio(value="Mecânica", label="Mecânica"),
                            ft.Radio(value="Hidráulica", label="Hidráulica"),
                            ft.Radio(value="Automação", label="Automação"),
                            ft.Text("", ref=equipe_erro_ref, color=ft.colors.RED),
                        ])
                    ),
                    ft.RadioGroup(
                        ref=classificacao_ref,
                        content=ft.Column([ 
                            ft.Text("Classificação"),
                            ft.Radio(value="Preventiva", label="Preventiva"),
                            ft.Radio(value="Corretiva", label="Corretiva"),
                            ft.Radio(value="Preditiva", label="Preditiva"),
                            ft.Radio(value="Melhoria", label="Melhoria"),
                            ft.Text("", ref=classificacao_erro_ref, color=ft.colors.RED),
                        ])
                    ),
                ]),
                ft.Row([ 
                    ft.RadioGroup(
                        ref=status_ref,
                        content=ft.Row([ 
                            ft.Text("Status"),
                            ft.Radio(value="Em aberto", label="Em aberto"),
                            ft.Radio(value="Encerrada", label="Encerrada"),
                            ft.Text("", ref=status_erro_ref, color=ft.colors.RED),
                        ])
                    ),
                ]),
                ft.Row([ 
                    ft.ElevatedButton("Salvar", on_click=cadastrar_ordem),
                    ft.ElevatedButton("Limpar", on_click=limpar_campos),
                    ft.ElevatedButton("Fechar", on_click=fechar_dialogo),
                ])
            ]
        ),
        ref=cadastro_dialog_ref,
    )

    page.overlay.append(cadastro_dialog)

    def abrir_dialogo():
        cadastro_dialog_ref.current.open = True
        page.update()

    return abrir_dialogo
