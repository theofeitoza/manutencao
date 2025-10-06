# ui_components.py
import flet as ft
from gerar_pdf import gerar_pdf_linha_dados
from databases import registrar_log
import sqlite3
from datetime import datetime

BANCO_DADOS_UNICO = "manutencao.db"

_dialogo_edicao_ordem_callback = None
_dialogo_edicao_equipamento_callback = None
_dialogo_edicao_peca_callback = None
_dialogo_edicao_funcionario_callback = None

def definir_callback_edicao(callback):
    """Define o callback para o diálogo de edição de ordens"""
    global _dialogo_edicao_ordem_callback
    _dialogo_edicao_ordem_callback = callback

def definir_callback_edicao_equipamento(callback):
    """Define o callback para o diálogo de edição de equipamentos"""
    global _dialogo_edicao_equipamento_callback
    _dialogo_edicao_equipamento_callback = callback

def definir_callback_edicao_peca(callback):
    """Define o callback para o diálogo de edição de peças"""
    global _dialogo_edicao_peca_callback
    _dialogo_edicao_peca_callback = callback

def definir_callback_edicao_funcionario(callback):
    """Define o callback para o diálogo de edição de funcionários"""
    global _dialogo_edicao_funcionario_callback
    _dialogo_edicao_funcionario_callback = callback

def criar_tabela(dados, colunas, excluir_callback, largura, ordenar_callback, tabela):
    """Cria uma tabela dinâmica com larguras de coluna mais adaptáveis e fontes maiores."""
    
    # Mapeamento de larguras de coluna para um visual mais limpo e previsível.
    # Ajustei os valores para acomodar melhor os cabeçalhos.

    def obter_botoes_acao(linha, tabela):
        botoes = [
            ft.IconButton(
                icon=ft.icons.PRINT,
                tooltip="Gerar PDF",
                on_click=lambda e, dados=linha: (print(f"Print clicked for {tabela} ID: {linha[0]}"), gerar_pdf_linha_dados(tabela, dados)),
            )
        ]
        
        if tabela == "ordens" and _dialogo_edicao_ordem_callback:
            botoes.append(ft.IconButton(
                icon=ft.icons.EDIT,
                tooltip="Editar",
                on_click=lambda e, dados=linha: (print(f"Edit clicked for {tabela} ID: {linha[0]}"), _dialogo_edicao_ordem_callback(dados)),
            ))
        elif tabela == "equipamentos" and _dialogo_edicao_equipamento_callback:
            botoes.append(ft.IconButton(
                icon=ft.icons.EDIT,
                tooltip="Editar",
                on_click=lambda e, dados=linha: (print(f"Edit clicked for {tabela} ID: {linha[0]}"), _dialogo_edicao_equipamento_callback(dados)),
            ))
        elif tabela == "pecas" and _dialogo_edicao_peca_callback:
            botoes.append(ft.IconButton(
                icon=ft.icons.EDIT,
                tooltip="Editar",
                on_click=lambda e, dados=linha: (print(f"Edit clicked for {tabela} ID: {linha[0]}"), _dialogo_edicao_peca_callback(dados)),
            ))
        elif tabela == "funcionarios" and _dialogo_edicao_funcionario_callback:
            botoes.append(ft.IconButton(
                icon=ft.icons.EDIT,
                tooltip="Editar",
                on_click=lambda e, dados=linha: (print(f"Edit clicked for {tabela} ID: {linha[0]}"), _dialogo_edicao_funcionario_callback(dados)),
            ))
        
        botoes.append(ft.IconButton(
            icon=ft.icons.DELETE,
            tooltip="Excluir",
            on_click=lambda e, id_registro=linha[0]: (print(f"Delete clicked for {tabela} ID: {id_registro}"), excluir_callback(id_registro)),
        ))
        
        return botoes

    # Construir as colunas do DataTable
    data_columns = []
    
    for titulo in colunas:
        col_key = titulo.lower().replace(" ", "_")
        
        data_columns.append(
            ft.DataColumn(
                ft.Text(titulo, size=18),
                on_sort=lambda e, coluna=titulo.lower(): ordenar_callback(coluna),
                tooltip=titulo,
            )
        )
    
    data_columns.append(
        ft.DataColumn(
            ft.Text("Ações", size=18),
            tooltip="Ações",
            on_sort=None,
        )
    )

    # Construir as linhas do DataTable
    data_rows = []
    for linha_dados in dados:
        cells = []
        for i, campo in enumerate(linha_dados):
            col_name = colunas[i].lower().replace(" ", "_")
            
            formatted_value = str(campo) if campo is not None else ""

            if col_name in ["data_criacao", "data_realizacao", "data_inicio_execucao", "data_fim_execucao"] and campo:
                try:
                    date_part = campo.split(" ")[0]
                    dt_obj = datetime.strptime(date_part, "%Y-%m-%d")
                    formatted_value = dt_obj.strftime("%d/%m/%Y")
                except ValueError:
                    formatted_value = str(campo)
            elif col_name in ["horario_abertura", "horario_fechamento"] and campo:
                try:
                    dt_obj = datetime.fromisoformat(campo)
                    formatted_value = dt_obj.strftime("%H:%M:%S")
                except ValueError:
                    formatted_value = str(campo)
            elif col_name in ["custo", "custo_unitario"] and campo:
                try:
                    cost_value = float(campo)
                    formatted_value = f"R$ {cost_value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                except (ValueError, TypeError):
                    formatted_value = str(campo) if campo is not None else ""
            
            max_chars = 40
            if col_name in ["descricao_defeito", "descricao", "email"]:
                max_chars = 50
            if len(formatted_value) > max_chars:
                 formatted_value = formatted_value[:max_chars-3] + "..."


            cells.append(
                ft.DataCell(
                    ft.Container(
                        content=ft.Text(
                            value=formatted_value,
                            size=18,
                            overflow=ft.TextOverflow.ELLIPSIS,
                            max_lines=1,
                            tooltip=str(campo) if campo is not None else ""
                        ) # Adiciona a largura fixa aqui
                    )
                )
            )
        
        cells.append(
            ft.DataCell(
                ft.Row(
                    obter_botoes_acao(linha_dados, tabela),
                    spacing=0,
                )
            )
        )
        data_rows.append(ft.DataRow(cells=cells))

    return ft.DataTable(
        columns=data_columns,
        rows=data_rows,
        heading_row_color="#E0E0E0",
        data_row_color={"hovered": "#ECEFF1"},
        border=ft.border.all(2, ft.colors.GREY_300),
        border_radius=ft.border_radius.all(10),
        vertical_lines=ft.border.BorderSide(1, ft.colors.GREY_300),
        horizontal_lines=ft.border.BorderSide(1, ft.colors.GREY_300),
        column_spacing=5,
        width=largura, # Largura da tabela principal continua dinâmica
    )