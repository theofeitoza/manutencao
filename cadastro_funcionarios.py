import flet as ft
from databases import salvar_funcionarios  # Ajuste o import se necessário

def criar_dialogo_funcionario(page: ft.Page, atualizar_tabela_callback):
    # Referências para os campos
    nome_completo_ref = ft.Ref[ft.TextField]()
    documento_ref = ft.Ref[ft.TextField]()
    telefone_ref = ft.Ref[ft.TextField]()
    email_ref = ft.Ref[ft.TextField]()
    funcao_ref = ft.Ref[ft.TextField]()
    equipe_ref = ft.Ref[ft.RadioGroup]()
    cargo_ref = ft.Ref[ft.RadioGroup]()
    funcao_erro_ref = ft.Ref[ft.Text]()
    equipe_erro_ref = ft.Ref[ft.Text]()
    cadastro_dialog_ref = ft.Ref[ft.AlertDialog]()

    def cadastrar_colaborador(e):
        nome_completo = nome_completo_ref.current.value.strip()
        documento = documento_ref.current.value.strip()
        telefone = telefone_ref.current.value.strip()
        email = email_ref.current.value.strip()
        funcao = funcao_ref.current.value
        equipe = equipe_ref.current.value
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
            funcao_erro_ref.current.value = "Selecione uma função"
            campos_invalidos = True
        else:
            funcao_erro_ref.current.value = None

        if not equipe:
            equipe_erro_ref.current.value = "Selecione uma equipe"
            campos_invalidos = True
        else:
            equipe_erro_ref.current.value = None

        if not cargo:
            funcao_erro_ref.current.value = "Selecione um cargo"
            campos_invalidos = True
        else:
            funcao_erro_ref.current.value = None

        page.update()

        if campos_invalidos:
            return

        # Chamar a função para salvar no banco de dados
        id_gerado = salvar_funcionarios(
            nome_completo, documento, telefone, email, funcao, equipe, cargo
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
        cargo_ref.current.value = None
        nome_completo_ref.current.error_text = None
        documento_ref.current.error_text = None
        telefone_ref.current.error_text = None
        email_ref.current.error_text = None
        funcao_erro_ref.current.value = None
        equipe_erro_ref.current.value = None
        page.update()

    def fechar_dialogo(e):
        cadastro_dialog_ref.current.open = False
        page.update()

    cadastro_dialog = ft.AlertDialog(
        modal=True,
        content=ft.Column(
            [
                ft.Text("Cadastro de Colaborador", size=20, weight=ft.FontWeight.BOLD),
                ft.TextField(label="Nome Completo", ref=nome_completo_ref),
                ft.TextField(label="Documento (RG)", ref=documento_ref),
                ft.TextField(label="Telefone", ref=telefone_ref),
                ft.TextField(label="Email", ref=email_ref),
                ft.TextField(label="Função", ref=funcao_ref),
                ft.Row(
                    [
                        ft.RadioGroup(
                            ref=cargo_ref,
                            content=ft.Column(
                                [
                                    ft.Text("Cargo"),
                                    ft.Radio(value="Líder", label="Líder"),
                                    ft.Radio(value="Gerente", label="Gerente"),
                                    ft.Radio(value="Supervisor", label="Supervisor"),
                                    ft.Radio(value="Encarregado", label="Encarregado"),
                                    ft.Text("", ref=funcao_erro_ref, color=ft.colors.RED),
                                ]
                            ),
                        ),
                        ft.RadioGroup(
                            ref=equipe_ref,
                            content=ft.Column(
                                [
                                    ft.Text("Equipe"),
                                    ft.Radio(value="Elétrica", label="Elétrica"),
                                    ft.Radio(value="Mecânica", label="Mecânica"),
                                    ft.Radio(value="Hidráulica", label="Hidráulica"),
                                    ft.Radio(value="Automação", label="Automação"),
                                    ft.Text("", ref=equipe_erro_ref, color=ft.colors.RED),
                                ]
                            ),
                        ),
                    ]
                ),
                ft.Row(
                    [
                        ft.ElevatedButton("Cadastrar", on_click=cadastrar_colaborador),
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
