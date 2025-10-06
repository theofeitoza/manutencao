import flet as ft
import sqlite3
from datetime import datetime
from databases import (
    registrar_abertura_ordem, registrar_fechamento_ordem,
    buscar_pecas_para_dropdown, associar_peca_a_ordem, buscar_pecas_por_ordem
)

def buscar_ordem_por_id(ordem_id: int):
    with sqlite3.connect("manutencao.db") as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM ordens WHERE id = ?", (ordem_id,))
        return cursor.fetchone()

def criar_dialogo_visualizacao_ordem(page: ft.Page):
    dialog_ref = ft.Ref[ft.AlertDialog]()
    campos_conteudo = ft.Ref[ft.Column]()

    pecas_dropdown = ft.Ref[ft.Dropdown]()
    quantidade_peca = ft.Ref[ft.TextField]()
    pecas_utilizadas_container = ft.Ref[ft.Column]()
    current_ordem_id = ft.Ref[int]()

    def fechar_dialogo(e):
        dialog_ref.current.open = False
        page.update()

    def atualizar_lista_pecas_usadas():
        pecas_utilizadas_container.current.controls.clear()
        pecas_usadas = buscar_pecas_por_ordem(current_ordem_id.current)
        if pecas_usadas:
            for peca, qtd in pecas_usadas:
                pecas_utilizadas_container.current.controls.append(
                    ft.Text(f"• {peca} (Qtd: {qtd})")
                )
        else:
            pecas_utilizadas_container.current.controls.append(
                ft.Text("Nenhuma peça adicionada ainda.", italic=True, color=ft.colors.GREY)
            )
        page.update()

    def get_pecas_options():
        pecas = buscar_pecas_para_dropdown()
        return [
            ft.dropdown.Option(key=str(peca[0]), text=f"{peca[1]} (Estoque: {peca[2]})")
            for peca in pecas
        ]

    def adicionar_peca(e):
        peca_id_str = pecas_dropdown.current.value
        qtd_str = quantidade_peca.current.value

        if not peca_id_str:
            page.snack_bar = ft.SnackBar(ft.Text("Selecione uma peça!", color="white"), bgcolor=ft.colors.RED)
            page.snack_bar.open = True
            page.update()
            return

        try:
            quantidade = int(qtd_str)
            if quantidade <= 0:
                raise ValueError
        except (ValueError, TypeError):
            page.snack_bar = ft.SnackBar(ft.Text("Insira uma quantidade válida!", color="white"), bgcolor=ft.colors.RED)
            page.snack_bar.open = True
            page.update()
            return

        peca_selecionada_texto = ""
        for option in pecas_dropdown.current.options:
            if option.key == peca_id_str:
                peca_selecionada_texto = option.text
                break

        if not peca_selecionada_texto:
            page.snack_bar = ft.SnackBar(ft.Text("Erro ao encontrar a peça selecionada.", color="white"), bgcolor=ft.colors.RED)
            page.snack_bar.open = True
            page.update()
            return

        estoque_atual = int(peca_selecionada_texto.split(": ")[1][:-1])

        if quantidade > estoque_atual:
            page.snack_bar = ft.SnackBar(ft.Text(f"Estoque insuficiente! Disponível: {estoque_atual}", color="white"), bgcolor=ft.colors.RED)
            page.snack_bar.open = True
            page.update()
            return

        associar_peca_a_ordem(current_ordem_id.current, int(peca_id_str), quantidade)

        quantidade_peca.current.value = ""
        pecas_dropdown.current.value = None
        pecas_dropdown.current.options = get_pecas_options()
        atualizar_lista_pecas_usadas()

        page.snack_bar = ft.SnackBar(ft.Text("Peça adicionada com sucesso!", color="white"), bgcolor=ft.colors.GREEN)
        page.snack_bar.open = True
        page.update()

    dialogo_visualizacao = ft.AlertDialog(
        ref=dialog_ref,
        modal=True,
        title=ft.Text("Detalhes da Ordem de Serviço", weight=ft.FontWeight.BOLD),
        content=ft.Column(
            [
                ft.Column(ref=campos_conteudo, scroll=ft.ScrollMode.ADAPTIVE, height=250),
                ft.Divider(),
                ft.Text("Adicionar Peças Utilizadas", weight=ft.FontWeight.BOLD),
                ft.Dropdown(ref=pecas_dropdown, hint_text="Selecione a peça"),
                ft.TextField(ref=quantidade_peca, label="Quantidade", keyboard_type=ft.KeyboardType.NUMBER),
                ft.ElevatedButton("Adicionar Peça", icon=ft.icons.ADD, on_click=adicionar_peca),
                ft.Divider(),
                ft.Text("Peças Já Utilizadas:", weight=ft.FontWeight.BOLD),
                ft.Column(ref=pecas_utilizadas_container, height=100, scroll=ft.ScrollMode.ADAPTIVE),
            ],
            height=600,
            width=500
        ),
        actions=[
            ft.TextButton("Fechar", on_click=fechar_dialogo)
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )

    page.overlay.append(dialogo_visualizacao)

    def abrir(dados_ordem: sqlite3.Row):
        current_ordem_id.current = dados_ordem['Id']
        campos_conteudo.current.controls.clear()

        for chave in dados_ordem.keys():
            valor = dados_ordem[chave]
            if 'data' in chave and valor:
                try: valor = datetime.fromisoformat(valor.split(" ")[0]).strftime("%d/%m/%Y")
                except: pass
            if chave == 'Custo' and valor is not None:
                valor = f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            campos_conteudo.current.controls.append(
                ft.Row([
                    ft.Text(f"{chave.replace('_', ' ').capitalize()}:", weight=ft.FontWeight.BOLD, width=150),
                    ft.Text(str(valor) if valor is not None else "N/A", selectable=True, expand=True),
                ])
            )

        pecas_dropdown.current.options = get_pecas_options()
        atualizar_lista_pecas_usadas()

        dialog_ref.current.open = True
        page.update()

    return abrir

def get_user_team(username):
    conn = sqlite3.connect("manutencao.db")
    cursor = conn.cursor()
    cursor.execute("SELECT f.equipe_id, e.nome_equipe FROM funcionarios f JOIN equipes e ON f.equipe_id = e.id WHERE f.email = ?", (username,))
    result = cursor.fetchone()
    conn.close()
    return result[1] if result else None


def check_credentials(username, password):
    conn = sqlite3.connect("manutencao.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM usuarios WHERE email = ? AND senha = ?", (username, password))
    user = cursor.fetchone()
    conn.close()
    if user:
        return get_user_team(username)
    return None

def main(page: ft.Page):
    page.title = "Visualizador de Ordens - Técnico"
    page.vertical_alignment = ft.MainAxisAlignment.START
    page.theme_mode = ft.ThemeMode.LIGHT

    orders_data_table_ref = ft.Ref[ft.DataTable]()
    orders_table_container = ft.Column(expand=True, scroll=ft.ScrollMode.ADAPTIVE)
    abrir_dialogo_visualizacao = criar_dialogo_visualizacao_ordem(page)

    def update_table_layout():
        largura_tabela_dinamica = page.width - 50 
        
        if orders_data_table_ref.current:
            orders_data_table_ref.current.width = largura_tabela_dinamica
            page.update()
        else:
            pass

    def get_orders_data_and_update_table(team_name):
        data_hoje = datetime.now().strftime("%Y-%m-%d")

        conn = sqlite3.connect("manutencao.db")
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, equipamento, descricao_defeito, Custo, equipe, criticidade, status, data_criacao,
                   Data_inicio_execucao, Data_fim_execucao,
                   Horario_abertura, Horario_fechamento
            FROM ordens
            WHERE equipe = ?
            AND status = 'Em aberto'
            AND DATE(?) BETWEEN DATE(Data_inicio_execucao) AND DATE(Data_fim_execucao)
            ORDER BY
                CASE criticidade
                    WHEN 'Alta' THEN 1
                    WHEN 'Média' THEN 2
                    WHEN 'Baixa' THEN 3
                    ELSE 4
                END
        """, (team_name, data_hoje))

        rows = cursor.fetchall()
        conn.close()

        columns = [
            ft.DataColumn(ft.Text("ID")),
            ft.DataColumn(ft.Text("Equipamento")),
            ft.DataColumn(ft.Text("Defeito")),
            ft.DataColumn(ft.Text("Custo")),
            ft.DataColumn(ft.Text("Equipe")),
            ft.DataColumn(ft.Text("Critic.")),
            ft.DataColumn(ft.Text("Status")),
            ft.DataColumn(ft.Text("Criação")),
            ft.DataColumn(ft.Text("Início")),
            ft.DataColumn(ft.Text("Fim")),
            ft.DataColumn(ft.Text("Abertura")),
            ft.DataColumn(ft.Text("Fechamento")),
            ft.DataColumn(ft.Text("Ações")),
        ]

        data_rows = []
        for order in rows:
            id_ordem, equipamento, defeito, custo, equipe, criticidade, status, data_criacao, data_inicio, data_fim, horario_abertura, horario_fechamento = order

            defeito_original = str(defeito) if defeito is not None else ""
            if len(defeito_original) > 60:
                defeito_display = defeito_original[:57] + "..."
            else:
                defeito_display = defeito_original

            custo_display = f"R$ {custo or 0:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

            data_criacao_display = datetime.strptime(data_criacao.split(" ")[0], "%Y-%m-%d").strftime("%d/%m/%Y") if data_criacao else "-"
            data_inicio_display = datetime.strptime(data_inicio, "%Y-%m-%d").strftime("%d/%m/%Y") if data_inicio else "-"
            data_fim_display = datetime.strptime(data_fim, "%Y-%m-%d").strftime("%d/%m/%Y") if data_fim else "-"

            data_rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(str(id_ordem))),
                        ft.DataCell(ft.Text(equipamento)),
                        ft.DataCell(
                            ft.Text(
                                value=defeito_display,
                                tooltip=defeito_original
                            )
                        ),
                        ft.DataCell(ft.Text(custo_display)),
                        ft.DataCell(ft.Text(equipe)),
                        ft.DataCell(ft.Text(criticidade)),
                        ft.DataCell(ft.Text(status)),
                        ft.DataCell(ft.Text(data_criacao_display)),
                        ft.DataCell(ft.Text(data_inicio_display)),
                        ft.DataCell(ft.Text(data_fim_display)),
                        ft.DataCell(ft.Text(horario_abertura if horario_abertura else "-")),
                        ft.DataCell(ft.Text(horario_fechamento if horario_fechamento else "-")),
                        ft.DataCell(
                            ft.Row([
                                ft.IconButton(icon=ft.icons.PLAY_ARROW, tooltip="Abrir e Visualizar Ordem", on_click=lambda e, oid=id_ordem: abrir_ordem_action(oid, team_name)),
                                ft.IconButton(icon=ft.icons.CHECK, tooltip="Fechar Ordem", on_click=lambda e, oid=id_ordem: fechar_ordem_action(oid, team_name)),
                            ])
                        )
                    ]
                )
            )

        orders_table_container.controls.clear()
        if not data_rows:
            orders_table_container.controls.append(
                ft.Container(
                    content=ft.Text("Nenhuma ordem de serviço programada para hoje.", size=18, text_align=ft.TextAlign.CENTER),
                    alignment=ft.alignment.center,
                    padding=50
                )
            )
        else:
            initial_table_width = page.width - 50

            tabela = ft.DataTable(
                ref=orders_data_table_ref,
                columns=columns,
                rows=data_rows,
                heading_row_color="#E0E0E0",
                data_row_color={"hovered": "#ECEFF1"},
                border=ft.border.all(2, "#B0BEC5"),
                border_radius=ft.border_radius.all(10),
                vertical_lines=ft.border.BorderSide(1, "#B0BEC5"),
                horizontal_lines=ft.border.BorderSide(1, "#B0BEC5"),
                column_spacing=5,
                show_checkbox_column=False,
                width=initial_table_width,
            )

            orders_table_container.controls.append(
                ft.Column(
                    [tabela],
                    scroll=ft.ScrollMode.ADAPTIVE,
                    expand=True,
                )
            )
        page.update()

    def show_orders_page(team_name):
        page.clean()
        page.add(
            ft.Column(
                [
                    ft.Text(f"Ordens de Manutenção - Equipe: {team_name}", size=24, weight=ft.FontWeight.BOLD),
                    ft.Divider(),
                    orders_table_container
                ],
                scroll=ft.ScrollMode.ADAPTIVE,
                expand=True,
                horizontal_alignment=ft.CrossAxisAlignment.STRETCH
            )
        )
        get_orders_data_and_update_table(team_name)
        page.on_resize = lambda e: update_table_layout()


    def abrir_ordem_action(ordem_id, team_name):
        registrar_abertura_ordem(ordem_id, datetime.now())
        get_orders_data_and_update_table(team_name)
        dados_da_ordem = buscar_ordem_por_id(ordem_id)
        if dados_da_ordem:
            abrir_dialogo_visualizacao(dados_da_ordem)

    def fechar_ordem_action(ordem_id, team_name):
        registrar_fechamento_ordem(ordem_id, datetime.now())
        get_orders_data_and_update_table(team_name)

    def login(e):
        team_name = check_credentials(username_field.value, password_field.value)
        if team_name:
            show_orders_page(team_name)
        else:
            error_text.value = "Usuário ou senha inválidos."
            page.update()

    username_field = ft.TextField(label="Usuário", width=300)
    password_field = ft.TextField(label="Senha", password=True, can_reveal_password=True, width=300)
    error_text = ft.Text("", color="#EF5350")

    page.add(
        ft.Container(
            expand=True,
            alignment=ft.alignment.center,
            content=ft.Column(
                [
                    ft.Text("Login do Técnico", size=30, weight=ft.FontWeight.BOLD),
                    username_field,
                    password_field,
                    ft.ElevatedButton("Entrar", on_click=login),
                    error_text,
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.CENTER,
            )
        )
    )

ft.app(target=main, port=8551)