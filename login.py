import flet as ft
import database  # Importa as funções do arquivo database.py

# Referências para os campos
email_ref = ft.Ref[ft.TextField]()
senha_ref = ft.Ref[ft.TextField]()

email_cadastro_ref = ft.Ref[ft.TextField]()
senha_cadastro_ref = ft.Ref[ft.TextField]()


# Função auxiliar para criar contêineres com gradiente
def criar_container(conteudo):
    return ft.Container(
        alignment=ft.alignment.center,
        width=500,
        height=400,
        content=conteudo,
        gradient=ft.LinearGradient(
            colors=[ft.colors.BLUE_700, ft.colors.BLACK],
            begin=ft.alignment.top_left,
            end=ft.alignment.bottom_right,
        ),
    )


# Tela de Login
def tela_login(page: ft.Page):
    page.clean()  # Limpa a tela atual

    # Adiciona os elementos de Login
    page.add(
        criar_container(
            ft.Column(
                controls=[
                    ft.Text(
                        "Login",
                        size=30,
                        weight=ft.FontWeight.BOLD,
                        text_align=ft.TextAlign.CENTER,
                        color=ft.colors.WHITE,
                    ),
                    ft.TextField(label="Email", ref=email_ref),
                    ft.TextField(label="Senha", password=True, ref=senha_ref),
                    ft.ElevatedButton("Entrar", on_click=entrar),
                    ft.TextButton("Cadastrar-se", on_click=lambda e: tela_cadastro(page)),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=20,
            )
        )
    )


# Tela de Cadastro
def tela_cadastro(page: ft.Page):
    page.clean()  # Limpa a tela atual

    # Adiciona os elementos de Cadastro
    page.add(
        criar_container(
            ft.Column(
                controls=[
                    ft.Text(
                        "Cadastro de Novo Usuário",
                        size=30,
                        weight=ft.FontWeight.BOLD,
                        text_align=ft.TextAlign.CENTER,
                        color=ft.colors.WHITE,
                    ),
                    ft.TextField(label="Email", ref=email_cadastro_ref),
                    ft.TextField(label="Senha", password=True, ref=senha_cadastro_ref),
                    ft.ElevatedButton("Cadastrar", on_click=lambda e: cadastrar(page)),
                    ft.TextButton("Voltar para o Login", on_click=lambda e: tela_login(page)),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=20,
            )
        )
    )


# Função de Login
def entrar(e):
    page = e.page
    email = email_ref.current.value.strip()
    senha = senha_ref.current.value.strip()

    if not email or not senha:
        mostrar_snackbar(page, "Preencha todos os campos!")
        return

    # Verifica usuário
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
        tela_login(page)  # Volta para o Login
    else:
        mostrar_snackbar(page, "Email já está em uso!")


# Função para exibir mensagens (SnackBar)
def mostrar_snackbar(page, mensagem):
    snack = ft.SnackBar(ft.Text(mensagem), open=True)
    page.snack_bar = snack
    page.update()


# Inicialização principal
def main(page: ft.Page):
    page.bgcolor = ft.colors.TRANSPARENT
    database.criar_tabela_usuarios()
    tela_login(page)  # Inicia com a tela de Login


ft.app(target=main)
