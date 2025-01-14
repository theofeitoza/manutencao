import flet as ft
import sqlite3
from cadastro_ordens import criar_dialogo_ordens
from cadastro_equipamentos import criar_dialogo_equipamentos
from cadastro_funcionarios import criar_dialogo_funcionario
from cadastro_pecas import criar_dialogo_pecas

# Caminho do banco de dados
BANCO_DADOS_UNICO = "manutencao.db"


def obter_conexao():
    return sqlite3.connect(BANCO_DADOS_UNICO)


def executar_query(query, parametros=(), fetchall=True):
    with sqlite3.connect(BANCO_DADOS_UNICO) as conexao:
        cursor = conexao.cursor()
        cursor.execute(query, parametros)
        if fetchall:
            return cursor.fetchall()
        else:
            conexao.commit()
            return cursor.fetchone()  # Retorna o primeiro resultado em vez de None



def ler_colunas_tabela(tabela):
    """Obtém os nomes das colunas de uma tabela."""
    with sqlite3.connect(BANCO_DADOS_UNICO) as conexao:
        cursor = conexao.cursor()
        cursor.execute(f"PRAGMA table_info({tabela})")
        return [linha[1] for linha in cursor.fetchall()]


def ler_dados_filtrados(tabela, colunas, coluna_ordem="id", direcao="ASC", filtro=""):
    """Consulta os dados aplicando filtro em todas as colunas."""
    filtro_query = " WHERE " + " OR ".join([f"{col} LIKE ?" for col in colunas]) if filtro else ""
    parametros = tuple(f"%{filtro}%" for _ in colunas) if filtro else ()
    query = f"SELECT * FROM {tabela}{filtro_query} ORDER BY {coluna_ordem} {direcao}"
    return executar_query(query, parametros)


def criar_tabela(dados, colunas, excluir_callback, largura, ordenar_callback):
    """Cria uma tabela dinâmica."""
    return ft.DataTable(
        columns=[
            ft.DataColumn(
                ft.Text(titulo),
                on_sort=lambda e, coluna=titulo.lower(): ordenar_callback(coluna),
            )
            for titulo in colunas
        ]
        + [ft.DataColumn(ft.Text("Ação"))],
        rows=[
            ft.DataRow(
                cells=[ft.DataCell(ft.Text(str(campo) if campo is not None else "")) for campo in linha]
                + [
                    ft.DataCell(
                        ft.IconButton(
                            icon=ft.icons.DELETE,
                            on_click=lambda e, id_registro=linha[0]: excluir_callback(id_registro),
                        )
                    )
                ]
            )
            for linha in dados
        ],
        width=largura,
    )


def main(page: ft.Page):
    page.title = "Sistema de Controle de Manutenção"
    page.scroll = "auto"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.window_maximized = True

    tabela_container = ft.Column()
    resumo_container = ft.Column()
    filtro_input = ft.TextField(hint_text="Buscar em qualquer coluna...", expand=False, on_change=lambda e: atualizar_aba())

    estado_ordenacao = {"coluna": "id", "direcao": "ASC"}
    tabela_selecionada = "ordens"

    def alternar_direcao(direcao_atual):
        return "DESC" if direcao_atual == "ASC" else "ASC"

    def atualizar_aba(coluna_ordem=None):
        tabela_container.controls.clear()
        largura_tabela = page.width * 0.8

        if coluna_ordem:
            if estado_ordenacao["coluna"] == coluna_ordem:
                estado_ordenacao["direcao"] = alternar_direcao(estado_ordenacao["direcao"])
            else:
                estado_ordenacao["coluna"] = coluna_ordem
                estado_ordenacao["direcao"] = "ASC"

        coluna = estado_ordenacao["coluna"]
        direcao = estado_ordenacao["direcao"]
        filtro = filtro_input.value.strip()
        colunas = ler_colunas_tabela(tabela_selecionada)
        dados = ler_dados_filtrados(tabela_selecionada, colunas, coluna, direcao, filtro)

        def excluir_callback(id_registro):
            executar_query(f"DELETE FROM {tabela_selecionada} WHERE id = ?", (id_registro,), fetchall=False)
            atualizar_aba()

        tabela_container.controls.append(
            criar_tabela(dados, colunas, excluir_callback, largura_tabela, lambda col: atualizar_aba(col))
        )
        page.update()

    def exibir_aba(aba):
        nonlocal tabela_selecionada
        tabela_selecionada = aba
        resumo_container.controls.clear()

        # Configurações para calcular os dados da barra de progresso
        progresso = 0
        texto_progresso = ""

        if aba == "ordens":
            total_ordens = executar_query("SELECT COUNT(*) FROM ordens", fetchall=False)[0]
            ordens_concluidas = executar_query("SELECT COUNT(*) FROM ordens WHERE status = 'Concluída'", fetchall=False)[0]
            progresso = ordens_concluidas / total_ordens if total_ordens > 0 else 0
            texto_progresso = f"Progresso: {ordens_concluidas}/{total_ordens} ordens concluídas"

        elif aba == "equipamentos":
            total_equipamentos = executar_query("SELECT COUNT(*) FROM equipamentos", fetchall=False)[0]
            equipamentos_ativos = executar_query("SELECT COUNT(*) FROM equipamentos WHERE status = 'Ativo'", fetchall=False)[0]
            progresso = equipamentos_ativos / total_equipamentos if total_equipamentos > 0 else 0
            texto_progresso = f"Progresso: {equipamentos_ativos}/{total_equipamentos} equipamentos ativos"

        elif aba == "funcionarios":
            total_funcionarios = executar_query("SELECT COUNT(*) FROM funcionarios", fetchall=False)[0]
            funcionarios_disponiveis = executar_query("SELECT COUNT(*) FROM funcionarios WHERE status = 'Disponível'", fetchall=False)[0]
            progresso = funcionarios_disponiveis / total_funcionarios if total_funcionarios > 0 else 0
            texto_progresso = f"Progresso: {funcionarios_disponiveis}/{total_funcionarios} funcionários disponíveis"

        elif aba == "pecas":
            total_pecas = executar_query("SELECT COUNT(*) FROM pecas", fetchall=False)[0]
            pecas_acima_minimo = executar_query("SELECT COUNT(*) FROM pecas WHERE quantidade > 50", fetchall=False)[0]
            progresso = pecas_acima_minimo / total_pecas if total_pecas > 0 else 0
            texto_progresso = f"Progresso: {pecas_acima_minimo}/{total_pecas} peças acima do estoque mínimo"

        # Adiciona a barra de progresso ao resumo, sem modificar os cartões
        resumo_container.controls.extend([
            ft.Text(texto_progresso, size=16, weight="bold"),
            ft.ProgressBar(value=progresso, width=page.width * 0.8),
            ft.Divider(),  # Para separar visualmente
        ])

        # Mantém os cartões e botões existentes
        if aba == "ordens":
            resumo_container.controls.append(
                ft.ElevatedButton("Abrir Cadastro de Ordens", on_click=lambda e: abrir_dialogo_ordens(), width=300)
            )
        elif aba == "equipamentos":
            resumo_container.controls.append(
                ft.ElevatedButton("Abrir Cadastro de Equipamentos", on_click=lambda e: abrir_dialogo_equipamentos(), width=300)
            )
        elif aba == "funcionarios":
            resumo_container.controls.append(
                ft.ElevatedButton("Abrir Cadastro de Funcionários", on_click=lambda e: abrir_dialogo_funcionario(), width=300)
            )
        elif aba == "pecas":
            resumo_container.controls.append(
                ft.ElevatedButton("Abrir Cadastro de Peças", on_click=lambda e: abrir_dialogo_pecas(), width=300)
            )

        atualizar_aba()
        page.update()

    abrir_dialogo_ordens = criar_dialogo_ordens(page, atualizar_tabela_callback=lambda: exibir_aba("ordens"))
    abrir_dialogo_equipamentos = criar_dialogo_equipamentos(page, atualizar_tabela_callback=lambda: exibir_aba("equipamentos"))
    abrir_dialogo_funcionario = criar_dialogo_funcionario(page, atualizar_tabela_callback=lambda: exibir_aba("funcionarios"))
    abrir_dialogo_pecas = criar_dialogo_pecas(page, atualizar_tabela_callback=lambda: exibir_aba("pecas"))

    page.add(
        ft.Column(
            [
                ft.Text("Sistema de Controle de Manutenção", size=32, weight="bold"),
                ft.Divider(thickness=1),
                ft.Row(
                    [
                        ft.ElevatedButton("Ordens", on_click=lambda e: exibir_aba("ordens")),
                        ft.ElevatedButton("Equipamentos", on_click=lambda e: exibir_aba("equipamentos")),
                        ft.ElevatedButton("Funcionários", on_click=lambda e: exibir_aba("funcionarios")),
                        ft.ElevatedButton("Estoque", on_click=lambda e: exibir_aba("pecas")),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                ft.Divider(thickness=1),
                ft.Row([filtro_input]),
                ft.Divider(thickness=1),
                resumo_container,
                ft.Divider(thickness=1),
                tabela_container,
            ]
        )
    )

    exibir_aba("ordens")


ft.app(main)
