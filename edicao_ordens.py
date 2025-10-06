import flet as ft
from databases import registrar_log, get_usuario_logado_id, buscar_equipes
import sqlite3
from datetime import datetime

BANCO_DADOS_UNICO = "manutencao.db"

def criar_dialogo_edicao_ordem(page: ft.Page, atualizar_tabela_callback):
    id_ordem_ref = ft.Ref[ft.Text]()
    dropdown_ref = ft.Ref[ft.Dropdown]()
    descricao_defeito_ref = ft.Ref[ft.TextField]()
    custo_ref = ft.Ref[ft.TextField]()
    equipe_ref = ft.Ref[ft.Dropdown]()
    classificacao_ref = ft.Ref[ft.RadioGroup]()
    criticidade_ref = ft.Ref[ft.RadioGroup]()
    status_ref = ft.Ref[ft.RadioGroup]()
    data_inicio_ref = ft.Ref[ft.DatePicker]()
    data_fim_ref = ft.Ref[ft.DatePicker]()
    data_inicio_display_ref = ft.Ref[ft.TextField]()
    data_fim_display_ref = ft.Ref[ft.TextField]()
    horario_abertura_display = ft.Ref[ft.TextField]()
    horario_fechamento_display = ft.Ref[ft.TextField]()
    edicao_dialog_ref = ft.Ref[ft.AlertDialog]()

    data_inicio_picker = ft.DatePicker(
        ref=data_inicio_ref, first_date=datetime(2023, 1, 1), last_date=datetime(2030, 12, 31)
    )
    data_fim_picker = ft.DatePicker(
        ref=data_fim_ref, first_date=datetime(2023, 1, 1), last_date=datetime(2030, 12, 31)
    )
    page.overlay.append(data_inicio_picker)
    page.overlay.append(data_fim_picker)

    data_inicio_display = ft.TextField(
        ref=data_inicio_display_ref, label="Data de Início da Execução", read_only=True
    )
    data_fim_display = ft.TextField(
        ref=data_fim_display_ref, label="Data de Fim da Execução", read_only=True
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

    def buscar_equipamentos():
        with sqlite3.connect(BANCO_DADOS_UNICO) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, nome FROM equipamentos")
            return cursor.fetchall()

    def salvar_edicao(e):
        data_fim_display.error_text = None
        id_ordem = id_ordem_ref.current.value.replace("ID: ", "")
        equipamento = dropdown_ref.current.value
        descricao_defeito = descricao_defeito_ref.current.value.strip()
        equipe = equipe_ref.current.value
        classificacao = classificacao_ref.current.value
        criticidade = criticidade_ref.current.value
        status = status_ref.current.value
        data_inicio = data_inicio_picker.value.strftime('%Y-%m-%d') if data_inicio_picker.value else None
        data_fim = data_fim_picker.value.strftime('%Y-%m-%d') if data_fim_picker.value else None

        if data_inicio and data_fim and (data_fim_picker.value < data_inicio_picker.value):
            data_fim_display.error_text = "Data final não pode ser anterior à inicial"
            page.update()
            return

        horario_abertura = horario_abertura_display.current.value.strip() if horario_abertura_display.current.value else None
        horario_fechamento = horario_fechamento_display.current.value.strip() if horario_fechamento_display.current.value else None

        with sqlite3.connect(BANCO_DADOS_UNICO) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE ordens 
                SET equipamento = ?, descricao_defeito = ?, equipe = ?, 
                    classificacao = ?, criticidade = ?, status = ?, 
                    Data_inicio_execucao = ?, Data_fim_execucao = ?,
                    Horario_abertura = ?, Horario_fechamento = ? 
                WHERE id = ?
            """, (equipamento, descricao_defeito, equipe, classificacao, criticidade, status,
                  data_inicio, data_fim,
                  horario_abertura, horario_fechamento,
                  id_ordem))
            conn.commit()

        registrar_log(id_ordem, "EDICAO", f"Ordem editada - Status: {status}", get_usuario_logado_id())
        atualizar_tabela_callback()
        fechar_dialogo(None)
        page.snack_bar = ft.SnackBar(ft.Text(f"Ordem {id_ordem} editada com sucesso!"))
        page.snack_bar.open = True
        page.update()

    def fechar_dialogo(e):
        edicao_dialog_ref.current.open = False
        page.update()

    edicao_dialog = ft.AlertDialog(
        modal=True,
        content=ft.Column(
            [
                ft.Text("Editar Ordem de Serviço", size=50, color=ft.colors.BLACK, weight=ft.FontWeight.BOLD),
                ft.Text("ID da Ordem:", ref=id_ordem_ref, size=16, weight=ft.FontWeight.BOLD),
                ft.Dropdown(
                    ref=dropdown_ref,
                    label="Selecione um Equipamento",
                    options=[ft.dropdown.Option(f"{eq[1]} (ID: {eq[0]})") for eq in buscar_equipamentos()],
                ),
                ft.TextField(adaptive=True, label="Descrição do defeito", max_length=400, multiline=True, ref=descricao_defeito_ref),
                ft.TextField(
                    ref=custo_ref,
                    label="Custo Total das Peças (R$)",
                    read_only=True,
                    border=ft.InputBorder.NONE
                ),
                ft.Row([
                    data_inicio_display,
                    ft.IconButton(icon=ft.icons.CALENDAR_MONTH, tooltip="Selecionar data de início", on_click=lambda _: data_inicio_picker.pick_date()),
                ]),
                ft.Row([
                    data_fim_display,
                    ft.IconButton(icon=ft.icons.CALENDAR_MONTH, tooltip="Selecionar data de fim", on_click=lambda _: data_fim_picker.pick_date()),
                ]),
                ft.TextField(label="Horário Abertura (ISO)", ref=horario_abertura_display, read_only=True),
                ft.TextField(label="Horário Fechamento (ISO)", ref=horario_fechamento_display, read_only=True),
                ft.Dropdown(
                    ref=equipe_ref,
                    label="Equipe",
                    options=[ft.dropdown.Option(key=eq[1], text=eq[1]) for eq in buscar_equipes()],
                ),
                ft.Row([
                    ft.RadioGroup(
                        ref=classificacao_ref,
                        content=ft.Column([
                            ft.Text("Classificação"),
                            ft.Radio(value="Preventiva", label="Preventiva"),
                            ft.Radio(value="Corretiva", label="Corretiva"),
                            ft.Radio(value="Preditiva", label="Preditiva"),
                            ft.Radio(value="Melhoria", label="Melhoria"),
                        ])
                    ),
                    ft.RadioGroup(
                        ref=criticidade_ref,
                        content=ft.Column([
                            ft.Text("Criticidade"),
                            ft.Radio(value="Baixa", label="Baixa"),
                            ft.Radio(value="Média", label="Média"),
                            ft.Radio(value="Alta", label="Alta"),
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
                        ])
                    ),
                ]),
                ft.Row([
                    ft.ElevatedButton("Salvar", on_click=salvar_edicao),
                    ft.ElevatedButton("Fechar", on_click=fechar_dialogo),
                ])
            ],
            scroll=ft.ScrollMode.ADAPTIVE, height=600,
        ),
        ref=edicao_dialog_ref,
    )

    page.overlay.append(edicao_dialog)

    def abrir_dialogo_com_dados(dados_ordem):
        id_ordem_ref.current.value = f"ID: {dados_ordem[0]}"
        dropdown_ref.current.value = dados_ordem[1]
        descricao_defeito_ref.current.value = dados_ordem[2]
        custo_ref.current.value = f"R$ {dados_ordem[3] or 0.0:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        equipe_ref.current.value = dados_ordem[4]
        classificacao_ref.current.value = dados_ordem[5]
        criticidade_ref.current.value = dados_ordem[6]
        status_ref.current.value = dados_ordem[7]

        if dados_ordem[9]:
            try:
                data_obj_inicio = datetime.strptime(dados_ordem[9], '%Y-%m-%d')
                data_inicio_picker.value = data_obj_inicio
                data_inicio_display.value = data_obj_inicio.strftime("%d/%m/%Y")
            except (ValueError, TypeError):
                data_inicio_display.value = ""
                data_inicio_picker.value = None
        else:
            data_inicio_display.value = ""
            data_inicio_picker.value = None

        if dados_ordem[10]:
            try:
                data_obj_fim = datetime.strptime(dados_ordem[10], '%Y-%m-%d')
                data_fim_picker.value = data_obj_fim
                data_fim_display.value = data_obj_fim.strftime("%d/%m/%Y")
            except (ValueError, TypeError):
                data_fim_display.value = ""
                data_fim_picker.value = None
        else:
            data_fim_display.value = ""
            data_fim_picker.value = None

        horario_abertura_display.current.value = dados_ordem[11] if dados_ordem[11] else ""
        horario_fechamento_display.current.value = dados_ordem[12] if dados_ordem[12] else ""

        edicao_dialog_ref.current.open = True
        page.update()

    return abrir_dialogo_com_dados