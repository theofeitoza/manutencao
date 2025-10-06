import flet as ft
import databases

email_ref = ft.Ref[ft.TextField]()
senha_ref = ft.Ref[ft.TextField]()
email_cadastro_ref = ft.Ref[ft.TextField]()
senha_cadastro_ref = ft.Ref[ft.TextField]()

def criar_container(conteudo):
    return ft.Container(
        alignment=ft.alignment.center,
        width=500,
        height=450,
        content=conteudo,
        padding=30,
        border_radius=20,
        bgcolor=ft.colors.WHITE,
        border=ft.border.all(1, ft.colors.GREY_300),
        shadow=ft.BoxShadow(
            blur_radius=10,
            spread_radius=2,
            color="rgba(0, 0, 0, 0.15)",
            offset=ft.Offset(0, 8),
        ),
    )

def tela_login(page: ft.Page, on_login_sucesso):
    page.window_maximized = True
    page.clean()

    senha_visivel = {"value": False}

    def alternar_visibilidade_senha(e):
        senha_visivel["value"] = not senha_visivel["value"]
        senha_ref.current.password = not senha_visivel["value"]
        botao_visibilidade.icon = ft.icons.VISIBILITY_OFF if senha_visivel["value"] else ft.icons.VISIBILITY
        page.update()

    botao_visibilidade = ft.IconButton(
        icon=ft.icons.VISIBILITY,
        on_click=alternar_visibilidade_senha,
        tooltip="Mostrar/ocultar senha"
    )

    page.add(
        ft.Container(
            expand=True,
            alignment=ft.alignment.center,
            bgcolor=ft.colors.WHITE,
            content=criar_container(
                ft.Column(
                    controls=[
                        ft.Text("Login", size=30, weight=ft.FontWeight.BOLD,
                                text_align=ft.TextAlign.CENTER, color=ft.colors.BLACK),
                        ft.TextField(label="Email", ref=email_ref, color="black", prefix_icon=ft.icons.EMAIL),
                        ft.TextField(
                            label="Senha",
                            color="black",
                            password=True,
                            ref=senha_ref,
                            suffix=botao_visibilidade,
                            prefix_icon=ft.icons.LOCK
                        ),
                        ft.ElevatedButton("Entrar", on_click=lambda e: entrar(e, on_login_sucesso)),
                        ft.ElevatedButton("Cadastrar-se", on_click=lambda e: tela_cadastro(page, on_login_sucesso)),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=20,
                )
            )
        )
    )

def tela_cadastro(page: ft.Page, on_login_sucesso):
    page.clean()

    senha_visivel = {"value": False}

    def alternar_visibilidade_senha(e):
        senha_visivel["value"] = not senha_visivel["value"]
        senha_cadastro_ref.current.password = not senha_visivel["value"]
        botao_visibilidade.icon = ft.icons.VISIBILITY_OFF if senha_visivel["value"] else ft.icons.VISIBILITY
        page.update()

    botao_visibilidade = ft.IconButton(
        icon=ft.icons.VISIBILITY,
        on_click=alternar_visibilidade_senha,
        tooltip="Mostrar/ocultar senha"
    )

    page.add(
        ft.Container(
            expand=True,
            alignment=ft.alignment.center,
            bgcolor=ft.colors.WHITE,
            content=criar_container(
                ft.Column(
                    controls=[
                        ft.Text("Cadastro de Novo Usuário", size=30, weight=ft.FontWeight.BOLD,
                                text_align=ft.TextAlign.CENTER, color=ft.colors.BLACK),
                        ft.TextField(label="Email", ref=email_cadastro_ref, prefix_icon=ft.icons.EMAIL,),
                        ft.TextField(
                            label="Senha",
                            password=True,
                            ref=senha_cadastro_ref,
                            suffix=botao_visibilidade,
                            prefix_icon=ft.icons.LOCK,
                        ),
                        ft.ElevatedButton("Cadastrar", on_click=lambda e: cadastrar(page, on_login_sucesso)),
                        ft.ElevatedButton("Voltar para o Login", on_click=lambda e: tela_login(page, on_login_sucesso)),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=20,
                )
            )
        )
    )

def entrar(e, on_login_sucesso):
    page = e.page
    email = email_ref.current.value.strip()
    senha = senha_ref.current.value.strip()

    if not email or not senha:
        mostrar_snackbar(page, "Preencha todos os campos!")
        return

    usuario = databases.buscar_usuario(email)
    if usuario and usuario[2] == senha:
        databases.set_usuario_logado_id(usuario[0])
        mostrar_snackbar(page, "Login bem-sucedido!")
        on_login_sucesso()
    else:
        mostrar_snackbar(page, "Email ou senha incorretos!")

def cadastrar(page, on_login_sucesso):
    email = email_cadastro_ref.current.value.strip()
    senha = senha_cadastro_ref.current.value.strip()

    if not email or not senha:
        mostrar_snackbar(page, "Preencha todos os campos!")
        return

    if databases.cadastrar_usuario(email, senha):
        mostrar_snackbar(page, "Usuário cadastrado com sucesso!")
        tela_login(page, on_login_sucesso)
    else:
        mostrar_snackbar(page, "Email já está em uso!")

def mostrar_snackbar(page, mensagem):
    snack = ft.SnackBar(ft.Text(mensagem), open=True)
    page.snack_bar = snack
    page.update()

