import flet as ft
from databases import salvar_ordens, registrar_log, get_usuario_logado_id, buscar_equipes
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

    dropdown_ref = ft.Ref[ft.Dropdown]()
    descricao_defeito_ref = ft.Ref[ft.TextField]()
    equipe_ref = ft.Ref[ft.Dropdown]()
    classificacao_ref = ft.Ref[ft.RadioGroup]()
    criticidade_ref = ft.Ref[ft.RadioGroup]()
    status_ref = ft.Ref[ft.RadioGroup]()
    data_inicio_ref = ft.Ref[ft.DatePicker]()
    data_fim_ref = ft.Ref[ft.DatePicker]()
    data_inicio_display_ref = ft.Ref[ft.TextField]()
    data_fim_display_ref = ft.Ref[ft.TextField]()
    equipe_erro_ref = ft.Ref[ft.Text]()
    classificacao_erro_ref = ft.Ref[ft.Text]()
    criticidade_erro_ref = ft.Ref[ft.Text]()
    status_erro_ref = ft.Ref[ft.Text]()
    cadastro_dialog_ref = ft.Ref[ft.AlertDialog]()

    data_inicio_picker = ft.DatePicker(
        ref=data_inicio_ref,
        first_date=datetime(2023, 1, 1),
        last_date=datetime(2030, 12, 31),
    )
    data_fim_picker = ft.DatePicker(
        ref=data_fim_ref,
        first_date=datetime(2023, 1, 1),
        last_date=datetime(2030, 12, 31),
    )
    page.overlay.append(data_inicio_picker)
    page.overlay.append(data_fim_picker)

    data_inicio_display = ft.TextField(
        ref=data_inicio_display_ref,
        label="Data de Início da Execução",
        read_only=True,
        hint_text="Selecione a data de início",
    )
    data_fim_display = ft.TextField(
        ref=data_fim_display_ref,
        label="Data de Fim da Execução",
        read_only=True,
        hint_text="Selecione a data de término",
    )

    def on_start_date_change(e):
        if data_inicio_picker.value:
            data_inicio_display.value = data_inicio_picker.value.strftime("%d/%m/%Y")
            if data_fim_picker.value and data_fim_picker.value < data_inicio_picker.value:
                data_fim_picker.value = data_inicio_picker.value
                data_fim_display.value = data_inicio_picker.value.strftime("%d/%m/%Y")
            page.update()

    def on_end_date_change(e):
        if data_fim_picker.value:
            data_fim_display.value = data_fim_picker.value.strftime("%d/%m/%Y")
            page.update()

    data_inicio_picker.on_change = on_start_date_change
    data_fim_picker.on_change = on_end_date_change

    def atualizar_dropdown_equipamentos():
        dropdown_ref.current.options = [
            ft.dropdown.Option(f"{equipamento[1]} (ID: {equipamento[0]})")
            for equipamento in buscar_equipamentos()
        ]
        page.update()

    def atualizar_dropdown_equipes():
        equipes = buscar_equipes()
        equipe_ref.current.options = [
            ft.dropdown.Option(key=equipe[1], text=equipe[1])
            for equipe in equipes
        ]
        page.update()

    def cadastrar_ordem(e):
        descricao_defeito_ref.current.error_text = None
        data_inicio_display.error_text = None
        data_fim_display.error_text = None
        equipe_erro_ref.current.value = None
        classificacao_erro_ref.current.value = None
        criticidade_erro_ref.current.value = None
        status_erro_ref.current.value = None

        equipamento = dropdown_ref.current.value
        descricao_defeito = descricao_defeito_ref.current.value.strip()
        equipe = equipe_ref.current.value
        classificacao = classificacao_ref.current.value
        criticidade = criticidade_ref.current.value
        status = status_ref.current.value
        data_inicio = data_inicio_picker.value.strftime("%Y-%m-%d") if data_inicio_picker.value else None
        data_fim = data_fim_picker.value.strftime("%Y-%m-%d") if data_fim_picker.value else None
        campos_invalidos = False

        if not descricao_defeito:
            descricao_defeito_ref.current.error_text = "Preenchimento obrigatório"
            campos_invalidos = True
        if not data_inicio:
            data_inicio_display.error_text = "Selecione uma data de início"
            campos_invalidos = True
        if not data_fim:
            data_fim_display.error_text = "Selecione uma data de fim"
            campos_invalidos = True
        if data_inicio and data_fim and (data_fim_picker.value < data_inicio_picker.value):
            data_fim_display.error_text = "Data final não pode ser anterior à inicial"
            campos_invalidos = True
        if not equipamento:
            dropdown_ref.current.error_text = "Selecione um equipamento"
            campos_invalidos = True
        else:
            dropdown_ref.current.error_text = None
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
        if not criticidade:
            criticidade_erro_ref.current.value = "Selecione uma criticidade"
            campos_invalidos = True
        else:
            criticidade_erro_ref.current.value = None
        if not status:
            status_erro_ref.current.value = "Selecione um status"
            campos_invalidos = True
        else:
            status_erro_ref.current.value = None

        page.update()

        if campos_invalidos:
            return

        id_gerado = salvar_ordens(equipamento, descricao_defeito, equipe, classificacao, criticidade, status, data_inicio, data_fim)
        usuario_id = get_usuario_logado_id()
        registrar_log(id_gerado, "CRIACAO", f"Ordem criada para {equipamento}. Período: {data_inicio_display.value} a {data_fim_display.value}", usuario_id)

        atualizar_tabela_callback()
        fechar_dialogo(None)
        page.snack_bar = ft.SnackBar(ft.Text(f"Ordem de serviço gerada com sucesso! ID: {id_gerado}"))
        page.snack_bar.open = True
        page.update()
        limpar_campos(None)

    def limpar_campos(e):
        dropdown_ref.current.value = None
        descricao_defeito_ref.current.value = ""
        equipe_ref.current.value = None
        classificacao_ref.current.value = None
        criticidade_ref.current.value = None
        status_ref.current.value = None
        data_inicio_display.value = ""
        data_fim_display.value = ""
        data_inicio_picker.value = None
        data_fim_picker.value = None
        data_inicio_display.error_text = None
        data_fim_display.error_text = None
        descricao_defeito_ref.current.error_text = None
        dropdown_ref.current.error_text = None
        equipe_erro_ref.current.value = None
        classificacao_erro_ref.current.value = None
        criticidade_erro_ref.current.value = None
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
                    options=[ft.dropdown.Option(f"{eq[1]} (ID: {eq[0]})") for eq in buscar_equipamentos()],
                    error_text=""
                ),
                ft.TextField(adaptive=True, label="Descrição do defeito", max_length=400, multiline=True, ref=descricao_defeito_ref),
                ft.Row([
                    data_inicio_display,
                    ft.IconButton(icon=ft.icons.CALENDAR_MONTH, tooltip="Selecionar data de início", on_click=lambda _: data_inicio_picker.pick_date()),
                ]),
                ft.Row([
                    data_fim_display,
                    ft.IconButton(icon=ft.icons.CALENDAR_MONTH, tooltip="Selecionar data de fim", on_click=lambda _: data_fim_picker.pick_date()),
                ]),
                ft.Column([
                    ft.Dropdown(
                        ref=equipe_ref,
                        label="Equipe",
                        options=[ft.dropdown.Option(key=eq[1], text=eq[1]) for eq in buscar_equipes()],
                    ),
                    ft.Text("", ref=equipe_erro_ref, color=ft.colors.RED),
                ]),
                ft.Row([
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
                    ft.RadioGroup(
                        ref=criticidade_ref,
                        content=ft.Column([
                            ft.Text("Criticidade"),
                            ft.Radio(value="Baixa", label="Baixa"),
                            ft.Radio(value="Média", label="Média"),
                            ft.Radio(value="Alta", label="Alta"),
                            ft.Text("", ref=criticidade_erro_ref, color=ft.colors.RED),
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
            ],
            scroll=ft.ScrollMode.ADAPTIVE
        ),
        ref=cadastro_dialog_ref,
    )

    page.overlay.append(cadastro_dialog)

    def abrir_dialogo():
        atualizar_dropdown_equipamentos()
        atualizar_dropdown_equipes()
        limpar_campos(None)
        cadastro_dialog_ref.current.open = True
        page.update()

    return abrir_dialogo, atualizar_dropdown_equipamentos