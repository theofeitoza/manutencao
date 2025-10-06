import flet as ft
from databases import salvar_funcionarios, buscar_equipes

def criar_dialogo_funcionario(page: ft.Page, atualizar_tabela_callback):
    nome_completo_ref = ft.Ref[ft.TextField]()
    documento_ref = ft.Ref[ft.TextField]()
    telefone_ref = ft.Ref[ft.TextField]()
    email_ref = ft.Ref[ft.TextField]()
    funcao_ref = ft.Ref[ft.TextField]()
    equipe_ref = ft.Ref[ft.Dropdown]()
    cargo_ref = ft.Ref[ft.TextField]()
    cargo_erro_ref = ft.Ref[ft.Text]()
    cadastro_dialog_ref = ft.Ref[ft.AlertDialog]()

    def atualizar_dropdown_equipes():
        equipes = buscar_equipes()
        equipe_ref.current.options = [
            ft.dropdown.Option(key=str(equipe[0]), text=equipe[1])
            for equipe in equipes
        ]
        page.update()

    def cadastrar_colaborador(e):
        nome_completo = nome_completo_ref.current.value.strip()
        documento = documento_ref.current.value.strip()
        telefone = telefone_ref.current.value.strip()
        email = email_ref.current.value.strip()
        funcao = funcao_ref.current.value
        equipe_id = equipe_ref.current.value
        cargo = cargo_ref.current.value
        campos_invalidos = False

        if not nome_completo:
            nome_completo_ref.current.error_text = "Preenchimento obrigatório"
            campos_invalidos = True
        else:
            nome_completo_ref.current.error_text = None

        if not documento:
            documento_ref.current.error_text = "Preenchimento obrigatório"
            campos_invalidos = True
        else:
            documento_ref.current.error_text = None

        if not telefone:
            telefone_ref.current.error_text = "Preenchimento obrigatório"
            campos_invalidos = True
        else:
            telefone_ref.current.error_text = None

        if not email:
            email_ref.current.error_text = "Preenchimento obrigatório"
            campos_invalidos = True
        else:
            email_ref.current.error_text = None

        if not funcao:
            funcao_ref.current.error_text = "Preenchimento obrigatório"
            campos_invalidos = True
        else:
            funcao_ref.current.error_text = None

        if not equipe_id:
            equipe_ref.current.error_text = "Selecione uma equipe"
            campos_invalidos = True
        else:
            equipe_ref.current.error_text = None

        if not cargo:
            cargo_ref.current.error_text = "Preenchimento obrigatório"
            campos_invalidos = True
        else:
            cargo_ref.current.error_text = None


        page.update()

        if campos_invalidos:
            return

        id_gerado = salvar_funcionarios(
            nome_completo, documento, telefone, email, funcao, equipe_id, cargo
        )

        atualizar_tabela_callback()
        
        fechar_dialogo(None)
        page.snack_bar = ft.SnackBar(ft.Text(f"Cadastro realizado com sucesso! ID: {id_gerado}"))
        page.snack_bar.open = True
        page.update()
        limpar_campos(None)

    def limpar_campos(e):
        nome_completo_ref.current.value = ""
        documento_ref.current.value = ""
        telefone_ref.current.value = ""
        email_ref.current.value = ""
        funcao_ref.current.value = None
        equipe_ref.current.value = None
        cargo_ref.current.value = ""
        nome_completo_ref.current.error_text = None
        documento_ref.current.error_text = None
        telefone_ref.current.error_text = None
        email_ref.current.error_text = None
        funcao_ref.current.error_text = None
        equipe_ref.current.error_text = None
        cargo_ref.current.error_text = None
        page.update()

    def fechar_dialogo(e):
        cadastro_dialog_ref.current.open = False
        page.update()

    cadastro_dialog = ft.AlertDialog(
        modal=True,
        content=ft.Column(
            [
                ft.Text("Cadastro de Colaborador", size=20, weight=ft.FontWeight.BOLD),
                ft.TextField(label="Nome Completo", ref=nome_completo_ref, error_text=""),
                ft.TextField(label="Documento (RG)", ref=documento_ref, error_text=""),
                ft.TextField(label="Telefone", ref=telefone_ref, error_text=""),
                ft.TextField(label="Email", ref=email_ref, error_text=""),
                ft.TextField(label="Função", ref=funcao_ref, error_text=""),
                ft.Dropdown(
                    ref=equipe_ref,
                    label="Selecione a Equipe",
                    options=[
                        ft.dropdown.Option(key=str(equipe[0]), text=equipe[1])
                        for equipe in buscar_equipes()
                    ],
                    error_text="",
                ),
                ft.TextField(label="Cargo", ref=cargo_ref, error_text=""),
                ft.Row(
                    [
                        ft.ElevatedButton("Cadastrar", on_click=cadastrar_colaborador),
                        ft.ElevatedButton("Limpar", on_click=limpar_campos),
                        ft.ElevatedButton("Fechar", on_click=fechar_dialogo),
                    ]
                ),
            ],
            scroll=ft.ScrollMode.ADAPTIVE
        ),
        ref=cadastro_dialog_ref,
    )

    page.overlay.append(cadastro_dialog)

    def abrir_dialogo():
        atualizar_dropdown_equipes()
        cadastro_dialog_ref.current.open = True
        page.update()

    return abrir_dialogo