import flet as ft
from cadastro_ordens import criar_dialogo_ordens
from cadastro_equipamentos import criar_dialogo_equipamentos
from cadastro_funcionarios import criar_dialogo_funcionario
from cadastro_pecas import criar_dialogo_pecas
from edicao_ordens import criar_dialogo_edicao_ordem
from edicao_equipamentos import criar_dialogo_edicao_equipamento
from edicao_pecas import criar_dialogo_edicao_peca
from edicao_funcionarios import criar_dialogo_edicao_funcionario
from gerenciador_equipes import criar_gerenciador_equipes
from visualizador_logs import criar_visualizador_logs
from db_utils import executar_query, ler_colunas_tabela, ler_dados_filtrados 
from ui_components import criar_tabela, definir_callback_edicao, definir_callback_edicao_equipamento, definir_callback_edicao_peca, definir_callback_edicao_funcionario
from summary_cards import criar_cartoes_resumo
from databases import registrar_log, get_usuario_logado_id 

class ManagementView(ft.Column):
    def __init__(self, page: ft.Page, initial_tab: str = "ordens"): 
        super().__init__(expand=True, scroll=ft.ScrollMode.ADAPTIVE, spacing=5) 
        self.page = page

        self.tabela_container = ft.Column()
        self.resumo_container = ft.Column()
        self.filtro_input = ft.TextField(hint_text="Buscar em qualquer coluna...", expand=False, on_change=lambda e: self.atualizar_aba())

        self.estado_ordenacao = {"coluna": "id", "direcao": "ASC"}
        self.tabela_selecionada = initial_tab 

        self.abrir_dialogo_ordens, self.atualizar_dropdown_ordens = criar_dialogo_ordens(self.page, self.atualizar_tabela_callback_ordens)
        self.abrir_dialogo_equipamentos = criar_dialogo_equipamentos(self.page, self.atualizar_tabela_callback_equipamentos, on_equipment_added_callback=self.atualizar_dropdown_ordens)
        self.abrir_dialogo_funcionario = criar_dialogo_funcionario(self.page, self.atualizar_tabela_callback_funcionarios)
        self.abrir_dialogo_pecas = criar_dialogo_pecas(self.page, self.atualizar_tabela_callback_pecas)

        self.abrir_dialogo_edicao_ordem = criar_dialogo_edicao_ordem(self.page, self.atualizar_tabela_callback_ordens)
        self.abrir_dialogo_edicao_equipamento = criar_dialogo_edicao_equipamento(self.page, self.atualizar_tabela_callback_equipamentos)
        self.abrir_dialogo_edicao_peca = criar_dialogo_edicao_peca(self.page, self.atualizar_tabela_callback_pecas)
        self.abrir_dialogo_edicao_funcionario = criar_dialogo_edicao_funcionario(self.page, self.atualizar_tabela_callback_funcionarios)

        self.abrir_gerenciador_equipes = criar_gerenciador_equipes(self.page, self.atualizar_tabela_callback_funcionarios)

        self.abrir_visualizador_logs = criar_visualizador_logs(self.page)

        definir_callback_edicao(self.abrir_dialogo_edicao_ordem)
        definir_callback_edicao_equipamento(self.abrir_dialogo_edicao_equipamento)
        definir_callback_edicao_peca(self.abrir_dialogo_edicao_peca)
        definir_callback_edicao_funcionario(self.abrir_dialogo_edicao_funcionario)

        self.controls = [
            ft.Text("Sistema de Controle de Manutenção", size=32, weight="bold"),
            ft.Divider(thickness=1),
            ft.Row([self.filtro_input]),
            ft.Divider(thickness=1),
            self.resumo_container,
            ft.Divider(thickness=1),
            self.tabela_container,
        ]
        
        self.exibir_aba(self.tabela_selecionada) 

    def atualizar_tabela_callback_ordens(self):
        self.exibir_aba("ordens")
    def atualizar_tabela_callback_equipamentos(self):
        self.exibir_aba("equipamentos")
    def atualizar_tabela_callback_funcionarios(self):
        self.exibir_aba("funcionarios")
    def atualizar_tabela_callback_pecas(self):
        self.exibir_aba("pecas")

    def alternar_direcao(self, direcao_atual):
        return "DESC" if direcao_atual == "ASC" else "ASC"

    def atualizar_aba(self, coluna_ordem=None):
        self.tabela_container.controls.clear()
        largura_tabela = self.page.width 

        if coluna_ordem:
            if self.estado_ordenacao["coluna"] == coluna_ordem:
                self.estado_ordenacao["direcao"] = self.alternar_direcao(self.estado_ordenacao["direcao"])
            else:
                self.estado_ordenacao["coluna"] = coluna_ordem
                self.estado_ordenacao["direcao"] = "ASC"

        coluna = self.estado_ordenacao["coluna"]
        direcao = self.estado_ordenacao["direcao"]
        filtro = self.filtro_input.value.strip()
        colunas = ler_colunas_tabela(self.tabela_selecionada)
        
        dados = ler_dados_filtrados(self.tabela_selecionada, colunas, coluna, direcao, filtro) 

        print(f"Tabela selecionada: {self.tabela_selecionada}") 
        
        def excluir_callback(id_registro):
            if self.tabela_selecionada == "ordens":
                dados_ordem = executar_query(f"SELECT equipamento, descricao_defeito FROM {self.tabela_selecionada} WHERE id = ?", (id_registro,), return_type='one') 
                if dados_ordem:
                    equipamento = dados_ordem[0]
                    descricao = dados_ordem[1]
                    detalhes = f"Ordem excluída - Equipamento: {equipamento}, Descrição: {descricao}"
                    registrar_log(id_registro, "Exclusão", detalhes, get_usuario_logado_id())
            
            executar_query(f"DELETE FROM {self.tabela_selecionada} WHERE id = ?", (id_registro,), return_type=None)
            self.atualizar_aba()

        self.tabela_container.controls.append(
            criar_tabela(dados, colunas, excluir_callback, largura_tabela, lambda col: self.atualizar_aba(col), self.tabela_selecionada)
        )
        self.page.update()

    def exibir_aba(self, aba):
        self.tabela_selecionada = aba
        self.resumo_container.controls.clear()

        if aba == "ordens":
            self.resumo_container.controls.append(criar_cartoes_resumo("Total de Ordens", "ordens"))
            self.resumo_container.controls.append(ft.Divider())
            self.resumo_container.controls.append(
                ft.Row([
                    ft.ElevatedButton("Abrir Cadastro de Ordens", on_click=lambda e: self.abrir_dialogo_ordens(), width=250),
                    ft.ElevatedButton("Ver Histórico de Alterações", on_click=lambda e: self.abrir_visualizador_logs(), width=250),
                ], alignment=ft.MainAxisAlignment.CENTER)
            )

        elif aba == "equipamentos":
            self.resumo_container.controls.append(criar_cartoes_resumo("Total de Equipamentos", "equipamentos"))
            self.resumo_container.controls.append(ft.Divider())
            self.resumo_container.controls.append(
                ft.Row([
                ft.ElevatedButton("Abrir Cadastro de Equipamentos", on_click=lambda e: self.abrir_dialogo_equipamentos(), width=300)
                ], alignment=ft.MainAxisAlignment.CENTER)
            )

        elif aba == "funcionarios":
            self.resumo_container.controls.append(criar_cartoes_resumo("Total de Funcionários", "funcionarios"))
            self.resumo_container.controls.append(ft.Divider())
            self.resumo_container.controls.append(
                ft.Row([
                    ft.ElevatedButton("Abrir Cadastro de Funcionários", on_click=lambda e: self.abrir_dialogo_funcionario(), width=250),
                    ft.ElevatedButton("Gerenciar Equipes", on_click=lambda e: self.abrir_gerenciador_equipes(), width=200),
                ], alignment=ft.MainAxisAlignment.CENTER)
            )

        elif aba == "pecas":
            self.resumo_container.controls.append(criar_cartoes_resumo("Total de Peças", "pecas", mostrar_menores=True))
            self.resumo_container.controls.append(ft.Divider())
            self.resumo_container.controls.append(
                ft.Row([
                ft.ElevatedButton("Abrir Cadastro de Peças", on_click=lambda e: self.abrir_dialogo_pecas(), width=300)
                ], alignment=ft.MainAxisAlignment.CENTER)
            )
        
        self.atualizar_aba()
        self.page.update()

def main_interface_view(page: ft.Page, initial_tab: str = "ordens"):
    return ManagementView(page, initial_tab=initial_tab)