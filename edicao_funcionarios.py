import flet as ft
from databases import atualizar_funcionario, buscar_equipes
import sqlite3

BANCO_DADOS_UNICO = "manutencao.db"

def criar_dialogo_edicao_funcionario(page: ft.Page, atualizar_tabela_callback):
    """Cria o diálogo de edição de funcionários"""
    
    # Referências para os campos
    id_funcionario_ref = ft.Ref[ft.Text]()
    nome_completo_ref = ft.Ref[ft.TextField]()
    documento_ref = ft.Ref[ft.TextField]()
    telefone_ref = ft.Ref[ft.TextField]()
    email_ref = ft.Ref[ft.TextField]()
    funcao_ref = ft.Ref[ft.TextField]()
    equipe_ref = ft.Ref[ft.Dropdown]()
    cargo_ref = ft.Ref[ft.TextField]()
    edicao_dialog_ref = ft.Ref[ft.AlertDialog]()

    # Nova função para atualizar o dropdown de equipes
    def atualizar_dropdown_equipes():
        equipes = buscar_equipes()
        equipe_ref.current.options = [
            ft.dropdown.Option(key=str(equipe[0]), text=equipe[1])
            for equipe in equipes
        ]
        page.update()

    def salvar_edicao(e):
        # Obter os valores dos campos
        id_funcionario = id_funcionario_ref.current.value.replace("ID: ", "")
        nome_completo = nome_completo_ref.current.value.strip()
        email = email_ref.current.value.strip()
        funcao = funcao_ref.current.value.strip()
        equipe_id = equipe_ref.current.value
        cargo = cargo_ref.current.value.strip()

        # Validação para campos numéricos
        try:
            documento = int(documento_ref.current.value) if documento_ref.current.value else 0
            documento_ref.current.error_text = None
        except ValueError:
            documento_ref.current.error_text = "Apenas números são permitidos"
            page.update()
            return

        try:
            telefone = int(telefone_ref.current.value) if telefone_ref.current.value else 0
            telefone_ref.current.error_text = None
        except ValueError:
            telefone_ref.current.error_text = "Apenas números são permitidos"
            page.update()
            return

        # Atualizar o funcionário no banco de dados
        atualizar_funcionario(id_funcionario, nome_completo, documento, telefone, email, funcao, equipe_id, cargo)

        atualizar_tabela_callback()
        fechar_dialogo(None)
        page.snack_bar = ft.SnackBar(ft.Text(f"Funcionário {id_funcionario} editado com sucesso!"))
        page.snack_bar.open = True
        page.update()

    def fechar_dialogo(e):
        edicao_dialog_ref.current.open = False
        page.update()

    edicao_dialog = ft.AlertDialog(
        modal=True,
        content=ft.Column(
            [
                ft.Text("Editar Funcionário", size=50, color=ft.colors.BLACK, weight=ft.FontWeight.BOLD),
                ft.Text("ID do Funcionário:", ref=id_funcionario_ref, size=16, weight=ft.FontWeight.BOLD),
                ft.TextField(label="Nome Completo", ref=nome_completo_ref),
                ft.TextField(label="Documento", ref=documento_ref, keyboard_type=ft.KeyboardType.NUMBER),
                ft.TextField(label="Telefone", ref=telefone_ref, keyboard_type=ft.KeyboardType.NUMBER),
                ft.TextField(label="Email", ref=email_ref),
                ft.TextField(label="Função", ref=funcao_ref),
                ft.Dropdown(
                    ref=equipe_ref,
                    label="Equipe",
                    # A lista de opções será atualizada na função abrir_dialogo_com_dados
                    options=[]
                ),
                ft.TextField(label="Cargo", ref=cargo_ref),
                ft.Row([
                    ft.ElevatedButton("Salvar", on_click=salvar_edicao),
                    ft.ElevatedButton("Fechar", on_click=fechar_dialogo),
                ])
            ]
        ),
        ref=edicao_dialog_ref,
    )

    page.overlay.append(edicao_dialog)

    def abrir_dialogo_com_dados(dados_funcionario):
        # 1. ATUALIZAR O DROPDOWN DE EQUIPES ANTES DE ABRIR
        atualizar_dropdown_equipes()

        # 2. Preencher os campos com os dados do funcionário
        id_funcionario_ref.current.value = f"ID: {dados_funcionario[0]}"
        nome_completo_ref.current.value = dados_funcionario[1]
        documento_ref.current.value = str(dados_funcionario[2])
        telefone_ref.current.value = str(dados_funcionario[3])
        email_ref.current.value = dados_funcionario[4]
        funcao_ref.current.value = dados_funcionario[5]
        # O valor da equipe agora se refere ao novo dropdown atualizado
        equipe_ref.current.value = str(dados_funcionario[6]) if dados_funcionario[6] else None
        cargo_ref.current.value = dados_funcionario[7]

        edicao_dialog_ref.current.open = True
        page.update()

    return abrir_dialogo_com_dados