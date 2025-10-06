import flet as ft
from databases import atualizar_equipamento
import sqlite3

BANCO_DADOS_UNICO = "manutencao.db"

def criar_dialogo_edicao_equipamento(page: ft.Page, atualizar_tabela_callback):
    """Cria o diálogo de edição de equipamentos"""
    
    id_equipamento_ref = ft.Ref[ft.Text]()
    nome_ref = ft.Ref[ft.TextField]()
    descricao_ref = ft.Ref[ft.TextField]()
    modelo_fabricante_ref = ft.Ref[ft.TextField]()
    localizacao_ref = ft.Ref[ft.TextField]()
    custo_ref = ft.Ref[ft.TextField]()
    classe_ref = ft.Ref[ft.RadioGroup]()
    criticidade_ref = ft.Ref[ft.RadioGroup]()
    edicao_dialog_ref = ft.Ref[ft.AlertDialog]()

    def salvar_edicao(e):
        id_equipamento = id_equipamento_ref.current.value.replace("ID: ", "")
        nome = nome_ref.current.value.strip()
        descricao = descricao_ref.current.value.strip()
        modelo_fabricante = modelo_fabricante_ref.current.value.strip()
        localizacao = localizacao_ref.current.value.strip()
        custo = float(custo_ref.current.value) if custo_ref.current.value else 0.0
        classe = classe_ref.current.value
        criticidade = criticidade_ref.current.value

        atualizar_equipamento(id_equipamento, nome, descricao, modelo_fabricante, localizacao, custo, classe, criticidade)

        atualizar_tabela_callback()
        fechar_dialogo(None)
        page.snack_bar = ft.SnackBar(ft.Text(f"Equipamento {id_equipamento} editado com sucesso!"))
        page.snack_bar.open = True
        page.update()

    def fechar_dialogo(e):
        edicao_dialog_ref.current.open = False
        page.update()

    edicao_dialog = ft.AlertDialog(
        modal=True,
        content=ft.Column(
            [
                ft.Text("Editar Equipamento", size=50, color=ft.colors.BLACK, weight=ft.FontWeight.BOLD),
                ft.Text("ID do Equipamento:", ref=id_equipamento_ref, size=16, weight=ft.FontWeight.BOLD),
                ft.TextField(label="Nome", ref=nome_ref),
                ft.TextField(label="Descrição", ref=descricao_ref, multiline=True),
                ft.TextField(label="Modelo/Fabricante", ref=modelo_fabricante_ref),
                ft.TextField(label="Localização", ref=localizacao_ref),
                ft.TextField(label="Custo", ref=custo_ref),
                ft.Row([
                    ft.RadioGroup(
                        ref=classe_ref,
                        content=ft.Column([
                            ft.Text("Classe"),
                            ft.Radio(value="Elétrico", label="Elétrico"),
                            ft.Radio(value="Mecânico", label="Mecânico"),
                            ft.Radio(value="Hidráulico", label="Hidráulico"),
                        ])
                    ),
                    ft.RadioGroup(
                        ref=criticidade_ref,
                        content=ft.Column([
                            ft.Text("Criticidade"),
                            ft.Radio(value="Alta", label="Alta"),
                            ft.Radio(value="Média", label="Média"),
                            ft.Radio(value="Baixa", label="Baixa"),
                        ])
                    ),
                ]),
                ft.Row([
                    ft.ElevatedButton("Salvar", on_click=salvar_edicao),
                    ft.ElevatedButton("Fechar", on_click=fechar_dialogo),
                ])
            ]
        ),
        ref=edicao_dialog_ref,
    )

    page.overlay.append(edicao_dialog)

    def abrir_dialogo_com_dados(dados_equipamento):
        id_equipamento_ref.current.value = f"ID: {dados_equipamento[0]}"
        nome_ref.current.value = dados_equipamento[1]
        descricao_ref.current.value = dados_equipamento[2]
        modelo_fabricante_ref.current.value = dados_equipamento[3]
        localizacao_ref.current.value = dados_equipamento[4]
        custo_ref.current.value = str(dados_equipamento[5])
        classe_ref.current.value = dados_equipamento[6]
        criticidade_ref.current.value = dados_equipamento[7]

        edicao_dialog_ref.current.open = True
        page.update()

    return abrir_dialogo_com_dados

