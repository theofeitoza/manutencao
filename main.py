import flet as ft
from login import tela_login
from visualizacoes import main_interface_view 
from visualizacao_gantt import tela_gantt 
from dashboard import tela_dashboard 
from databases import criar_tabela_usuarios 

def app_launcher(page: ft.Page):
    page.clean()
    page.window.maximized = True
    page.title = "Sistema de Manutenção"
    page.theme_mode = ft.ThemeMode.LIGHT
    
    content_area = ft.Container(expand=True, alignment=ft.alignment.top_left, padding=10, bgcolor=ft.colors.WHITE)

    def change_view_drawer(e):
        selected_tab = e.control.data 
        
        if selected_tab == "dashboard":
            content_area.content = tela_dashboard(page)
        elif selected_tab == "ordens":
            content_area.content = main_interface_view(page, initial_tab="ordens")
        elif selected_tab == "equipamentos":
            content_area.content = main_interface_view(page, initial_tab="equipamentos")
        elif selected_tab == "funcionarios":
            content_area.content = main_interface_view(page, initial_tab="funcionarios")
        elif selected_tab == "pecas":
            content_area.content = main_interface_view(page, initial_tab="pecas")
        elif selected_tab == "gantt":
            content_area.content = tela_gantt(page)
        
        page.drawer.open = False 
        page.update() 

    page.drawer = ft.NavigationDrawer(
        controls=[
            ft.Container(height=12),
            ft.ListTile(
                leading=ft.Icon(ft.icons.DASHBOARD),
                title=ft.Text("Dashboard"),
                on_click=change_view_drawer,
                data="dashboard",
            ),
            ft.Divider(height=1, color=ft.colors.GREY_300),
            ft.ListTile(
                leading=ft.Icon(ft.icons.ASSIGNMENT),
                title=ft.Text("Ordens"),
                on_click=change_view_drawer,
                data="ordens",
            ),
            ft.Divider(height=1, color=ft.colors.GREY_300),
            ft.ListTile(
                leading=ft.Icon(ft.icons.HARDWARE),
                title=ft.Text("Equipamentos"),
                on_click=change_view_drawer,
                data="equipamentos",
            ),
            ft.Divider(height=1, color=ft.colors.GREY_300),
            ft.ListTile(
                leading=ft.Icon(ft.icons.PEOPLE),
                title=ft.Text("Funcionários"),
                on_click=change_view_drawer,
                data="funcionarios",
            ),
            ft.Divider(height=1, color=ft.colors.GREY_300),
            ft.ListTile(
                leading=ft.Icon(ft.icons.INVENTORY),
                title=ft.Text("Peças"),
                on_click=change_view_drawer,
                data="pecas",
            ),
            ft.Divider(height=1, color=ft.colors.GREY_300),
            ft.ListTile(
                leading=ft.Icon(ft.icons.TIMELINE),
                title=ft.Text("Gantt"),
                on_click=change_view_drawer,
                data="gantt",
            ),
        ]
    )

    page.snack_bar = ft.SnackBar(ft.Text(""), open=False)
    page.overlay.append(page.snack_bar)

    def open_drawer(e):
        page.drawer.open = True
        page.update()

    def iniciar_interface_principal():
        page.clean() 
        
        content_area.content = tela_dashboard(page)
        
        page.appbar = ft.AppBar(
            leading=ft.IconButton(
                ft.icons.MENU, 
                on_click=open_drawer
            ),
            title=ft.Text("Sistema de Manutenção"),
            center_title=False,
            bgcolor=ft.colors.SURFACE_VARIANT,
        )

        page.add(
            ft.Row(
                [
                    content_area,
                ],
                expand=True,
            )
        )
        page.update()

    tela_login(page, on_login_sucesso=iniciar_interface_principal)

ft.app(target=app_launcher)