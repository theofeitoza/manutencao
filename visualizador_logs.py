import flet as ft
import sqlite3
from databases import registrar_log

BANCO_DADOS_UNICO = "manutencao.db"

def criar_visualizador_logs(page: ft.Page):
    """Cria um visualizador de logs das alterações"""
    
    logs_container = ft.Column(scroll=ft.ScrollMode.AUTO)
    logs_dialog_ref = ft.Ref[ft.AlertDialog]()

    def carregar_logs():
        logs_container.controls.clear()
        
        with sqlite3.connect(BANCO_DADOS_UNICO) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT l.id, l.id_ordem, l.tipo_alteracao, l.detalhes_alteracao, 
                       l.data_alteracao, u.email
                FROM logs l
                LEFT JOIN usuarios u ON l.usuario_id = u.id
                ORDER BY l.data_alteracao DESC
                LIMIT 50
            """)
            logs = cursor.fetchall()

        if not logs:
            logs_container.controls.append(
                ft.Text("Nenhum log encontrado", size=16, color=ft.colors.GREY)
            )
        else:
            for log in logs:
                id_log, id_ordem, tipo, detalhes, data, usuario_email = log
                if tipo.upper() == "CRIACAO":
                    cor = ft.colors.GREEN
                elif tipo.upper() == "EDICAO":
                    cor = ft.colors.BLUE
                elif tipo.upper() == "EXCLUSAO":
                    cor = ft.colors.RED
                else:
                    cor = ft.colors.ORANGE
                
                usuario_display = usuario_email if usuario_email else "Sistema"
                
                logs_container.controls.append(
                    ft.Card(
                        content=ft.Container(
                            content=ft.Column([
                                ft.Row([
                                    ft.Text(f"Ordem #{id_ordem}", weight=ft.FontWeight.BOLD, size=16),
                                    ft.Text(tipo, color=cor, weight=ft.FontWeight.BOLD),
                                    ft.Text(data, size=12, color=ft.colors.GREY),
                                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                                ft.Text(detalhes, size=14),
                                ft.Row([
                                    ft.Icon(ft.icons.PERSON, size=16, color=ft.colors.GREY),
                                    ft.Text(f"Usuário: {usuario_display}", size=12, color=ft.colors.GREY),
                                ], spacing=5),
                            ]),
                            padding=10,
                        ),
                        margin=ft.margin.only(bottom=5),
                    )
                )
        
        page.update()

    def fechar_dialogo(e):
        logs_dialog_ref.current.open = False
        page.update()

    logs_dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("Histórico de Alterações", size=24, weight=ft.FontWeight.BOLD),
        content=ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.ElevatedButton("Atualizar", on_click=lambda e: carregar_logs()),
                    ft.ElevatedButton("Fechar", on_click=fechar_dialogo),
                ], alignment=ft.MainAxisAlignment.END),
                ft.Divider(),
                ft.Container(
                    content=logs_container,
                    height=400,
                    width=600,
                ),
            ]),
            width=650,
            height=500,
        ),
        ref=logs_dialog_ref,
    )

    page.overlay.append(logs_dialog)

    def abrir_logs():
        carregar_logs()
        logs_dialog_ref.current.open = True
        page.update()

    return abrir_logs

