import flet as ft
from databases import salvar_ordens  # Ajuste o import conforme necessário
import sqlite3
from datetime import datetime

BANCO_DADOS_UNICO = "manutencao.db"

def buscar_equipamentos():
    conexao = sqlite3.connect(BANCO_DADOS_UNICO)
    cursor = conexao.cursor()
    cursor.execute("SELECT id, nome FROM equipamentos")
    equipamentos = cursor.fetchall()
    conexao.close()
    return equipamentos

def criar_dialogo_ordens(page: ft.Page, atualizar_tabela_callback):
    page.theme_mode = ft.ThemeMode.LIGHT

    # Referências dos campos
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
    data_selecionada_ref = ft.Ref[ft.Text]()

    # DatePicker
    data_picker = ft.DatePicker(
        on_change=lambda e: atualizar_data()
    )

    def atualizar_data():
        if data_picker.value:
            data_selecionada_ref.current.value = f"Data selecionada: {data_picker.value.strftime('%Y-%m-%d')}"
            page.update()

    def cadastrar_ordem(e):
        equipamento = dropdown_ref.current.value
        descricao_defeito = descricao_defeito_ref.current.value.strip()
        tipo_manutencao = tipo_manutencao_ref.current.value.strip()
        equipe = equipe_ref.current.value
        classificacao = classificacao_ref.current.value
        status = status_ref.current.value
        data_selecionada = data_picker.value.strftime('%Y-%m-%d') if data_picker.value else None
        campos_invalidos = False

        # Validação
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

        if not equipe:
            equipe_erro_ref.current.value = "Selecione uma equipe"
            campos_invalidos = True

        if not classificacao:
            classificacao_erro_ref.current.value = "Selecione uma classificação"
            campos_invalidos = True

        if not status:
            status_erro_ref.current.value = "Selecione um status"
            campos_invalidos = True

        if not data_selecionada:
            data_selecionada_ref.current.value = "Data é obrigatória!"
            campos_invalidos = True

        page.update()

        if campos_invalidos:
            return

        # Salvar no banco
        id_gerado = salvar_ordens(
            equipamento, descricao_defeito, tipo_manutencao, equipe, classificacao, status, data_selecionada
        )

        atualizar_tabela_callback()

        fechar_dialogo(None)
        page.snack_bar = ft.SnackBar(ft.Text(f"Ordem cadastrada com sucesso! ID: {id_gerado}"))
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
        data_selecionada_ref.current.value = "Nenhuma data selecionada"
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
                    ref=descricao_defeito_ref,
                ),
                ft.TextField(
                    adaptive=True,
                    label="Tipo de manutenção",
                    max_length=50,
                    ref=tipo_manutencao_ref,
                ),
                ft.Text("Selecione a data"),
                ft.Row(
                    [
                        ft.ElevatedButton("Escolher Data", on_click=lambda _: data_picker.pick_date()),
                        ft.Text("Nenhuma data selecionada", ref=data_selecionada_ref),
                    ]
                ),
                ft.RadioGroup(
                    ref=equipe_ref,
                    content=ft.Column([
                        ft.Text("Equipe"),
                        ft.Radio(value="Elétrica", label="Elétrica"),
                        ft.Radio(value="Mecânica", label="Mecânica"),
                        ft.Radio(value="Hidráulica", label="Hidráulica"),
                        ft.Radio(value="Automação", label="Automação"),
                    ]),
                ),
                ft.RadioGroup(
                    ref=classificacao_ref,
                    content=ft.Column([
                        ft.Text("Classificação"),
                        ft.Radio(value="Preventiva", label="Preventiva"),
                        ft.Radio(value="Corretiva", label="Corretiva"),
                        ft.Radio(value="Preditiva", label="Preditiva"),
                        ft.Radio(value="Melhoria", label="Melhoria"),
                    ]),
                ),
                ft.RadioGroup(
                    ref=status_ref,
                    content=ft.Row([
                        ft.Text("Status"),
                        ft.Radio(value="Em aberto", label="Em aberto"),
                        ft.Radio(value="Encerrada", label="Encerrada"),
                    ]),
                ),
                ft.Row([
                    ft.ElevatedButton("Salvar", on_click=cadastrar_ordem),
                    ft.ElevatedButton("Limpar", on_click=limpar_campos),
                    ft.ElevatedButton("Fechar", on_click=fechar_dialogo),
                ]),
            ],
            scroll=True,
        ),
        ref=cadastro_dialog_ref,
    )

    page.overlay.append(cadastro_dialog)
    page.overlay.append(data_picker)

    def abrir_dialogo():
        cadastro_dialog_ref.current.open = True
        page.update()

    return abrir_dialogo
