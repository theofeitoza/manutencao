import flet as ft
from databases import atualizar_peca
import sqlite3

BANCO_DADOS_UNICO = "manutencao.db"

def criar_dialogo_edicao_peca(page: ft.Page, atualizar_tabela_callback):
    id_peca_ref = ft.Ref[ft.Text]()
    nome_peca_ref = ft.Ref[ft.TextField]()
    descricao_ref = ft.Ref[ft.TextField]()
    fabricante_ref = ft.Ref[ft.TextField]()
    dimensoes_ref = ft.Ref[ft.TextField]()
    peso_ref = ft.Ref[ft.TextField]()
    quantidade_ref = ft.Ref[ft.TextField]()
    custo_unitario_ref = ft.Ref[ft.TextField]()
    classe_ref = ft.Ref[ft.RadioGroup]()
    edicao_dialog_ref = ft.Ref[ft.AlertDialog]()

    def salvar_edicao(e):
        id_peca = id_peca_ref.current.value.replace("ID: ", "")
        nome_peca = nome_peca_ref.current.value.strip()
        descricao = descricao_ref.current.value.strip()
        fabricante = fabricante_ref.current.value.strip()
        dimensoes = dimensoes_ref.current.value.strip()
        peso = float(peso_ref.current.value.replace(',', '.')) if peso_ref.current.value else 0.0
        quantidade = int(quantidade_ref.current.value) if quantidade_ref.current.value else 0
        custo_unitario = float(custo_unitario_ref.current.value.replace(',', '.')) if custo_unitario_ref.current.value else 0.0
        classe = classe_ref.current.value

        atualizar_peca(id_peca, nome_peca, descricao, fabricante, dimensoes, peso, quantidade, classe, custo_unitario)

        atualizar_tabela_callback()
        fechar_dialogo(None)
        page.snack_bar = ft.SnackBar(ft.Text(f"Peça {id_peca} editada com sucesso!"))
        page.snack_bar.open = True
        page.update()

    def fechar_dialogo(e):
        edicao_dialog_ref.current.open = False
        page.update()

    edicao_dialog = ft.AlertDialog(
        modal=True,
        content=ft.Column(
            [
                ft.Text("Editar Peça", size=50, color=ft.colors.BLACK, weight=ft.FontWeight.BOLD),
                ft.Text("ID da Peça:", ref=id_peca_ref, size=16, weight=ft.FontWeight.BOLD),
                ft.TextField(label="Nome da Peça", ref=nome_peca_ref),
                ft.TextField(label="Descrição", ref=descricao_ref, multiline=True),
                ft.TextField(label="Fabricante", ref=fabricante_ref),
                ft.TextField(label="Dimensões", ref=dimensoes_ref),
                ft.TextField(label="Peso", ref=peso_ref, keyboard_type=ft.KeyboardType.NUMBER),
                ft.TextField(label="Quantidade", ref=quantidade_ref, keyboard_type=ft.KeyboardType.NUMBER),
                ft.TextField(
                    label="Custo Unitário (R$)", ref=custo_unitario_ref, 
                    keyboard_type=ft.KeyboardType.NUMBER,
                    input_filter=ft.InputFilter(allow=True, regex_string=r"[0-9.,]")
                ),
                ft.RadioGroup(
                    ref=classe_ref,
                    content=ft.Column([
                        ft.Text("Classe"),
                        ft.Radio(value="Elétrico", label="Elétrico"),
                        ft.Radio(value="Mecânico", label="Mecânico"),
                        ft.Radio(value="Hidráulico", label="Hidráulico"),
                        ft.Radio(value="Eletrônico", label="Eletrônico"),
                    ])
                ),
                ft.Row([
                    ft.ElevatedButton("Salvar", on_click=salvar_edicao),
                    ft.ElevatedButton("Fechar", on_click=fechar_dialogo),
                ])
            ],
            scroll=ft.ScrollMode.ADAPTIVE, height=600
        ),
        ref=edicao_dialog_ref,
    )

    page.overlay.append(edicao_dialog)

    def abrir_dialogo_com_dados(dados_peca):
        id_peca_ref.current.value = f"ID: {dados_peca[0]}"
        nome_peca_ref.current.value = dados_peca[1]
        descricao_ref.current.value = dados_peca[2]
        fabricante_ref.current.value = dados_peca[3]
        dimensoes_ref.current.value = dados_peca[4]
        peso_ref.current.value = str(dados_peca[5] or "")
        quantidade_ref.current.value = str(dados_peca[6] or "")
        classe_ref.current.value = dados_peca[7]
        custo_unitario_ref.current.value = str(dados_peca[8] or "")

        edicao_dialog_ref.current.open = True
        page.update()

    return abrir_dialogo_com_dados