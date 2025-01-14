import flet as ft
import database  # Importa as funções do arquivo database.py

# Referências para os campos
email_ref = ft.Ref[ft.TextField]()
senha_ref = ft.Ref[ft.TextField]()

email_cadastro_ref = ft.Ref[ft.TextField]()
senha_cadastro_ref = ft.Ref[ft.TextField]()


# Função auxiliar para criar contêineres simples
def criar_container(conteudo):
    return ft.Container(
        alignment=ft.alignment.center,
        width=500,
        height=400,
        content=conteudo,
        border_radius=10,  # Bordas arredondadas
        padding=20,
        shadow=ft.BoxShadow(blur_radius=10, color=ft.colors.BLACK12),  # Sombra suave
    )


# Tela de Login como Dialog
def dialog_login(page: ft.Page):
    def mostrar_cadastro(e):
        login_dialog.open = False  # Fecha o diálogo de login
        page.update()
        dialog_cadastro(page)  # Abre o diálogo de cadastro

    login_dialog = ft.AlertDialog(
        modal=True,
        content=criar_container(
            ft.Column(
                controls=[
                    ft.Text(
                        "Login",
                        size=30,
                        weight=ft.FontWeight.BOLD,
                        text_align=ft.TextAlign.CENTER,
                    ),
                    ft.TextField(label="Email", ref=email_ref),
                    ft.TextField(label="Senha", password=True, ref=senha_ref),
                    ft.ElevatedButton("Entrar", on_click=entrar),
                    ft.TextButton("Cadastrar-se", on_click=mostrar_cadastro),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=20,
            )
        ),
    )
    page.dialog = login_dialog
    login_dialog.open = True
    page.update()


# Tela de Cadastro como Dialog
def dialog_cadastro(page: ft.Page):
    def voltar_login(e):
        cadastro_dialog.open = False  # Fecha o diálogo de cadastro
        page.update()
        dialog_login(page)  # Abre o diálogo de login

    cadastro_dialog = ft.AlertDialog(
        modal=True,
        content=criar_container(
            ft.Column(
                controls=[
                    ft.Text(
                        "Cadastro de Novo Usuário",
                        size=30,
                        weight=ft.FontWeight.BOLD,
                        text_align=ft.TextAlign.CENTER,
                    ),
                    ft.TextField(label="Email", ref=email_cadastro_ref),
                    ft.TextField(label="Senha", password=True, ref=senha_cadastro_ref),
                    ft.ElevatedButton("Cadastrar", on_click=lambda e: cadastrar(page)),
                    ft.TextButton("Voltar para o Login", on_click=voltar_login),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=20,
            )
        ),
    )
    page.dialog = cadastro_dialog
    cadastro_dialog.open = True
    page.update()


# Função de Login
def entrar(e):
    page = e.page
    email = email_ref.current.value.strip()
    senha = senha_ref.current.value.strip()

    if not email or not senha:
        mostrar_snackbar(page, "Preencha todos os campos!")
        return

    usuario = database.buscar_usuario(email)
    if usuario and usuario[2] == senha:
        mostrar_snackbar(page, "Login bem-sucedido!")
    else:
        mostrar_snackbar(page, "Email ou senha incorretos!")


# Função de Cadastro
def cadastrar(page):
    email = email_cadastro_ref.current.value.strip()
    senha = senha_cadastro_ref.current.value.strip()

    if not email or not senha:
        mostrar_snackbar(page, "Preencha todos os campos!")
        return

    if database.cadastrar_usuario(email, senha):
        mostrar_snackbar(page, "Usuário cadastrado com sucesso!")
        dialog_login(page)  # Volta para o Login
    else:
        mostrar_snackbar(page, "Email já está em uso!")


# Função para exibir mensagens (SnackBar)
def mostrar_snackbar(page, mensagem):
    snack = ft.SnackBar(ft.Text(mensagem), open=True)
    page.snack_bar = snack
    page.update()


# Inicialização principal
def main(page: ft.Page):
    page.theme_mode = ft.ThemeMode.LIGHT  # Ativa o tema claro
    page.theme = ft.Theme(color_scheme_seed="blue")  # Opcional: define uma cor principal
    database.criar_tabela_usuarios()
    dialog_login(page)  # Abre a tela de Login


ft.app(target=main)
