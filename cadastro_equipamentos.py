import flet as ft
from databases import salvar_equipamentos  # Ajuste o import se necessário

def criar_dialogo_equipamentos(page: ft.Page, atualizar_tabela_callback):
    # Referências para os campos
    nome_equipamento_ref = ft.Ref[ft.TextField]()
    descricao_equipamento_ref = ft.Ref[ft.TextField]()
    modelo_fabricante_ref = ft.Ref[ft.TextField]()
    localizacao_ref = ft.Ref[ft.TextField]()
    custo_equipamento_ref = ft.Ref[ft.TextField]()
    classe_ref = ft.Ref[ft.RadioGroup]()
    criticidade_ref = ft.Ref[ft.RadioGroup]()
    classe_erro_ref = ft.Ref[ft.Text]()
    criticidade_erro_ref = ft.Ref[ft.Text]()
    cadastro_dialog_ref = ft.Ref[ft.AlertDialog]()

    def cadastrar_equipamento(e):
        nome_equipamento = nome_equipamento_ref.current.value.strip()
        descricao_equipamento = descricao_equipamento_ref.current.value.strip()
        modelo_fabricante = modelo_fabricante_ref.current.value.strip()
        localizacao = localizacao_ref.current.value.strip()
        custo = custo_equipamento_ref.current.value.strip()
        classe = classe_ref.current.value
        criticidade = criticidade_ref.current.value
        campos_invalidos = False

        if not nome_equipamento:
            nome_equipamento_ref.current.error_text = "Preenchimento obrigatório"
            campos_invalidos = True
        else:
            nome_equipamento_ref.current.error_text = None

        if not descricao_equipamento:
            descricao_equipamento_ref.current.error_text = "Preenchimento obrigatório"
            campos_invalidos = True
        else:
            descricao_equipamento_ref.current.error_text = None

        if not modelo_fabricante:
            modelo_fabricante_ref.current.error_text = "Preenchimento obrigatório"
            campos_invalidos = True
        else:
            modelo_fabricante_ref.current.error_text = None

        if not localizacao:
            localizacao_ref.current.error_text = "Preenchimento obrigatório"
            campos_invalidos = True
        else:
            localizacao_ref.current.error_text = None

        if not custo:
            custo_equipamento_ref.current.error_text = "Preenchimento obrigatório"
            campos_invalidos = True
        else:
            custo_equipamento_ref.current.error_text = None

        if not classe:
            classe_erro_ref.current.value = "Selecione uma classe"
            campos_invalidos = True
        else:
            classe_erro_ref.current.value = None

        if not criticidade:
            criticidade_erro_ref.current.value = "Selecione uma criticidade"
            campos_invalidos = True
        else:
            criticidade_erro_ref.current.value = None

        page.update()

        if campos_invalidos:
            return

        id_gerado = salvar_equipamentos(
            nome_equipamento, descricao_equipamento,
            modelo_fabricante, localizacao, custo, classe, criticidade
        )

        atualizar_tabela_callback()
        
        fechar_dialogo(None)
        page.snack_bar = ft.SnackBar(ft.Text(f"Cadastro realizado com sucesso! ID: {id_gerado}"))
        page.snack_bar.open = True
        page.update()
        limpar_campos(None)

    def limpar_campos(e):
        nome_equipamento_ref.current.value = ""
        descricao_equipamento_ref.current.value = ""
        modelo_fabricante_ref.current.value = ""
        localizacao_ref.current.value = ""
        custo_equipamento_ref.current.value = ""
        nome_equipamento_ref.current.error_text = None
        descricao_equipamento_ref.current.error_text = None
        modelo_fabricante_ref.current.error_text = None
        localizacao_ref.current.error_text = None
        custo_equipamento_ref.current.error_text = None
        classe_ref.current.value = None
        criticidade_ref.current.value = None
        classe_erro_ref.current.value = None
        criticidade_erro_ref.current.value = None
        page.update()

    def fechar_dialogo(e):
        cadastro_dialog_ref.current.open = False
        page.update()

    cadastro_dialog = ft.AlertDialog(
        modal=True,
        content=ft.Column(
            [
                ft.Text("Cadastro de Equipamentos", size=20, weight=ft.FontWeight.BOLD),
                ft.TextField(label="Nome do Equipamento", ref=nome_equipamento_ref),
                ft.TextField(label="Descrição do Equipamento", ref=descricao_equipamento_ref),
                ft.TextField(label="Modelo - Fabricante", ref=modelo_fabricante_ref),
                ft.TextField(label="Localização do Equipamento", ref=localizacao_ref),
                ft.TextField(label="Custo do Equipamento", ref=custo_equipamento_ref),
                ft.Row(
                    [
                        ft.RadioGroup(
                            ref=classe_ref,
                            content=ft.Column(
                                [
                                    ft.Text("Classe"),
                                    ft.Radio(value="Elétrico", label="Elétrico"),
                                    ft.Radio(value="Mecânico", label="Mecânico"),
                                    ft.Radio(value="Hidráulico", label="Hidráulico"),
                                    ft.Text("", ref=classe_erro_ref, color=ft.colors.RED),
                                ]
                            ),
                        ),
                        ft.RadioGroup(
                            ref=criticidade_ref,
                            content=ft.Column(
                                [
                                    ft.Text("Criticidade"),
                                    ft.Radio(value="Baixa", label="Baixa"),
                                    ft.Radio(value="Média", label="Média"),
                                    ft.Radio(value="Alta", label="Alta"),
                                    ft.Text("", ref=criticidade_erro_ref, color=ft.colors.RED),
                                ]
                            ),
                        ),
                    ]
                ),
                ft.Row(
                    [
                        ft.ElevatedButton("Cadastrar", on_click=cadastrar_equipamento),
                        ft.ElevatedButton("Limpar", on_click=limpar_campos),
                        ft.ElevatedButton("Fechar", on_click=fechar_dialogo),
                    ]
                ),
            ]
        ),
        ref=cadastro_dialog_ref,
    )

    page.overlay.append(cadastro_dialog)

    # Função para abrir o dialog
    def abrir_dialogo():
        cadastro_dialog_ref.current.open = True
        page.update()

    return abrir_dialogo
    
