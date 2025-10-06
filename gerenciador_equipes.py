import flet as ft
from databases import salvar_equipe, buscar_equipes, executar_query
import sqlite3

BANCO_DADOS_UNICO = "manutencao.db"

def criar_gerenciador_equipes(page: ft.Page, atualizar_tabela_callback):
    """Cria o gerenciador de equipes"""
    
    nome_equipe_ref = ft.Ref[ft.TextField]()
    equipes_container = ft.Column(scroll=ft.ScrollMode.ADAPTIVE)
    gerenciador_dialog_ref = ft.Ref[ft.AlertDialog]()

    def carregar_equipes():
        equipes_container.controls.clear()
        equipes = buscar_equipes()
        
        if not equipes:
            equipes_container.controls.append(
                ft.Text("Nenhuma equipe cadastrada", size=16, color=ft.colors.GREY)
            )
        else:
            for equipe in equipes:
                id_equipe, nome_equipe = equipe
                
                with sqlite3.connect(BANCO_DADOS_UNICO) as conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT nome_completo FROM funcionarios WHERE equipe_id = ?", (id_equipe,))
                    funcionarios = cursor.fetchall()
                
                funcionarios_nomes = [f[0] for f in funcionarios] if funcionarios else ["Nenhum funcionário"]
                
                equipes_container.controls.append(
                    ft.Card(
                        content=ft.Container(
                            content=ft.Column([
                                ft.Row([
                                    ft.Text(nome_equipe, weight=ft.FontWeight.BOLD, size=16),
                                    ft.IconButton(
                                        icon=ft.icons.DELETE,
                                        tooltip="Excluir equipe",
                                        on_click=lambda e, eq_id=id_equipe: excluir_equipe(eq_id),
                                    ),
                                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                                ft.Text(f"Funcionários: {', '.join(funcionarios_nomes)}", size=12, color=ft.colors.GREY),
                            ]),
                            padding=10,
                        ),
                        margin=ft.margin.only(bottom=5),
                    )
                )
        
        page.update()

    def cadastrar_equipe(e):
        nome_equipe = nome_equipe_ref.current.value.strip()
        
        if not nome_equipe:
            page.snack_bar = ft.SnackBar(ft.Text("Digite o nome da equipe!"))
            page.snack_bar.open = True
            page.update()
            return
        
        try:
            salvar_equipe(nome_equipe)
            nome_equipe_ref.current.value = ""
            carregar_equipes()
            atualizar_tabela_callback()
            page.snack_bar = ft.SnackBar(ft.Text(f"Equipe '{nome_equipe}' criada com sucesso!"))
            page.snack_bar.open = True
            page.update()
        except Exception as ex:
            page.snack_bar = ft.SnackBar(ft.Text(f"Erro ao criar equipe: {str(ex)}"))
            page.snack_bar.open = True
            page.update()

    def excluir_equipe(id_equipe):
        try:
            with sqlite3.connect(BANCO_DADOS_UNICO) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM funcionarios WHERE equipe_id = ?", (id_equipe,))
                count = cursor.fetchone()[0]
                
                if count > 0:
                    page.snack_bar = ft.SnackBar(ft.Text("Não é possível excluir equipe com funcionários!"))
                    page.snack_bar.open = True
                    page.update()
                    return
                
                cursor.execute("DELETE FROM equipes WHERE id = ?", (id_equipe,))
                conn.commit()
            
            carregar_equipes()
            atualizar_tabela_callback()
            page.snack_bar = ft.SnackBar(ft.Text("Equipe excluída com sucesso!"))
            page.snack_bar.open = True
            page.update()
        except Exception as ex:
            page.snack_bar = ft.SnackBar(ft.Text(f"Erro ao excluir equipe: {str(ex)}"))
            page.snack_bar.open = True
            page.update()

    def fechar_dialogo(e):
        gerenciador_dialog_ref.current.open = False
        page.update()

    gerenciador_dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("Gerenciar Equipes", size=24, weight=ft.FontWeight.BOLD),
        content=ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.TextField(
                        ref=nome_equipe_ref,
                        label="Nome da Equipe",
                        expand=True,
                    ),
                    ft.ElevatedButton("Criar", on_click=cadastrar_equipe),
                ]),
                ft.Divider(),
                ft.Text("Equipes Cadastradas:", weight=ft.FontWeight.BOLD),
                ft.Container(
                    content=equipes_container,
                    height=300,
                    width=500,
                ),
                ft.Row([
                    ft.ElevatedButton("Atualizar", on_click=lambda e: carregar_equipes()),
                    ft.ElevatedButton("Fechar", on_click=fechar_dialogo),
                ], alignment=ft.MainAxisAlignment.END),
            ]),
            width=550,
            height=450,
        ),
        ref=gerenciador_dialog_ref,
    )

    page.overlay.append(gerenciador_dialog)

    def abrir_gerenciador():
        carregar_equipes()
        gerenciador_dialog_ref.current.open = True
        page.update()

    return abrir_gerenciador