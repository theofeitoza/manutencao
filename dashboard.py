import flet as ft
from datetime import datetime, timedelta, date
from db_utils import executar_query, buscar_top_equipamentos_com_ordens, buscar_ordens_por_equipe, buscar_ordens_por_classificacao, buscar_custo_por_classificacao, buscar_custo_por_data, _get_date_range_sql, buscar_horas_manutencao_total
import math
from summary_cards import criar_cartao_mtbf, calcular_mtbf_equipamento

class DashboardView(ft.Column):
    def __init__(self, page: ft.Page):
        super().__init__(expand=True, scroll=ft.ScrollMode.ADAPTIVE, spacing=15)
        self.page = page

        self.selected_period = "last_12_months"


        self.average_time_card = self.create_average_time_card(self.selected_period)
        self.mtbf_card = criar_cartao_mtbf(self.selected_period)
        self.disponibilidade_card = self.create_disponibilidade_card(self.selected_period)

        self.orders_opened_30_days_card = self.create_example_card(
            "Ordens Abertas", 
            "SELECT COUNT(Id) FROM ordens WHERE DATE(Data_criacao)",
            period=self.selected_period
        )
        self.orders_closed_30_days_card = self.create_example_card(
            "Ordens Encerradas", 
            "SELECT COUNT(Id) FROM ordens WHERE Status = 'Encerrada' AND DATE(Data_fim_execucao)",
            period=self.selected_period
        )
        
        self.GRAPH_CARD_WIDTH = 600 
        self.GRAPH_CARD_HEIGHT = 350 

        self.top_equipment_chart_card = self.create_top_equipment_chart_card(self.selected_period)
        self.orders_by_team_chart_card = self.create_orders_by_team_chart_card(self.selected_period) 
        self.orders_by_classification_chart_card = self.create_orders_by_classification_chart_card(self.selected_period) 
        self.cost_by_date_chart_card = self.create_cost_by_date_chart_card(self.selected_period)

        self.summary_cards_row = ft.Row(wrap=True, spacing=20, alignment=ft.MainAxisAlignment.START)
        self.all_charts_row_1 = ft.Row(wrap=True, spacing=20, alignment=ft.MainAxisAlignment.START, expand=True) 
        self.all_charts_row_2 = ft.Row(wrap=True, spacing=20, alignment=ft.MainAxisAlignment.START, expand=True) 

        self.period_dropdown = ft.Dropdown(
            label="Período dos Gráficos",
            options=[
                ft.dropdown.Option("last_week", text="Última Semana"),
                ft.dropdown.Option("last_month", text="Último Mês"),
                ft.dropdown.Option("last_6_months", text="Últimos 6 Meses"),
                ft.dropdown.Option("last_12_months", text="Últimos 12 Meses"),
            ],
            value=self.selected_period, 
            on_change=self.on_period_change,
            width=200
        )

        self.controls = [
            ft.Text("Dashboard de Manutenção", size=28, weight=ft.FontWeight.BOLD),
            ft.Divider(thickness=1),
            self.summary_cards_row, 
            ft.Divider(thickness=1),
            ft.Row([ 
                ft.Text("Gráficos e Estatísticas", size=22, weight=ft.FontWeight.BOLD, expand=True),
                self.period_dropdown,
            ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
            self.all_charts_row_1, 
            ft.Divider(thickness=1),
            ft.Text("Gráfico de Custos por Data (R$)", size=22, weight=ft.FontWeight.BOLD), 
            self.all_charts_row_2, 
        ]
        
        self.update_dashboard()

    def on_period_change(self, e):
        self.selected_period = e.control.value
        self.update_dashboard()

    def update_dashboard(self):
        self.average_time_card = self.create_average_time_card(self.selected_period)
        self.mtbf_card = criar_cartao_mtbf(self.selected_period)
        self.disponibilidade_card = self.create_disponibilidade_card(self.selected_period)
        
        self.orders_opened_30_days_card = self.create_example_card(
            "Ordens Abertas", 
            "SELECT COUNT(Id) FROM ordens WHERE DATE(Data_criacao)",
            period=self.selected_period
        )
        self.orders_closed_30_days_card = self.create_example_card(
            "Ordens Encerradas", 
            "SELECT COUNT(Id) FROM ordens WHERE Status = 'Encerrada' AND DATE(Data_fim_execucao)",
            period=self.selected_period
        )
        
        self.top_equipment_chart_card = self.create_top_equipment_chart_card(self.selected_period)
        self.orders_by_team_chart_card = self.create_orders_by_team_chart_card(self.selected_period) 
        self.orders_by_classification_chart_card = self.create_orders_by_classification_chart_card(self.selected_period) 
        self.cost_by_date_chart_card = self.create_cost_by_date_chart_card(self.selected_period) 

        self.summary_cards_row.controls.clear()
        self.summary_cards_row.controls.extend([
            self.average_time_card,
            self.mtbf_card,
            self.disponibilidade_card,
            self.orders_opened_30_days_card,
            self.orders_closed_30_days_card,
        ])

        self.all_charts_row_1.controls.clear()
        self.all_charts_row_1.controls.extend([
            self.top_equipment_chart_card,
            self.orders_by_team_chart_card,
            self.orders_by_classification_chart_card, 
        ])
        
        self.all_charts_row_2.controls.clear()
        self.all_charts_row_2.controls.extend([
            self.cost_by_date_chart_card, 
        ])
        
        self.page.update() 
    
    def create_average_time_card(self, period: str):
        date_range_sql = _get_date_range_sql(period)
        
        query = f"""
            SELECT Horario_abertura, Horario_fechamento
            FROM ordens
            WHERE Status = 'Encerrada'
            AND Horario_abertura IS NOT NULL
            AND Horario_fechamento IS NOT NULL
            AND {date_range_sql.replace('Data_criacao', 'Data_fim_execucao')}
        """
        results = executar_query(query)

        total_duration_seconds = 0
        completed_orders_count = 0

        for abertura_str, fechamento_str in results:
            try:
                abertura_dt = datetime.strptime(abertura_str, '%Y-%m-%d %H:%M:%S')
                fechamento_dt = datetime.strptime(fechamento_str, '%Y-%m-%d %H:%M:%S')

                if fechamento_dt >= abertura_dt:
                    duration = fechamento_dt - abertura_dt
                    total_duration_seconds += duration.total_seconds()
                    completed_orders_count += 1
            except ValueError as e:
                print(f"Erro ao parsear horário em Dashboard para MTTR: {abertura_str} ou {fechamento_str} - {e}")
                continue

        average_time_str = "N/A"
        average_seconds = 0
        if completed_orders_count > 0:
            average_seconds = total_duration_seconds / completed_orders_count
            
            hours = int(average_seconds // 3600)
            minutes = int((average_seconds % 3600) // 60)
            seconds = int(average_seconds % 60)
            
            average_time_str = f"{hours}h {minutes}m {seconds}s"
        else:
            average_time_str = "Sem dados no período selecionado"

        mttr_horas = average_seconds / 3600.0 if average_seconds > 0 else 0.0

        return ft.Card(
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.Text("MTTR", size=24, weight="bold", color=ft.colors.BLACK),
                        ft.Text(average_time_str, size=26, weight="bold", color=ft.colors.BLUE_800),
                        ft.Text(f"({completed_orders_count} ordens encerradas)", size=12, color=ft.colors.GREY_600)
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=5
                ),
                width=280,
                height=150,
                bgcolor=ft.colors.BLUE_50,
                border_radius=10,
                border=ft.border.all(1, ft.colors.GREY_300), 
                alignment=ft.alignment.center,
                padding=15
            ),
            data=mttr_horas
        )


    def create_example_card(self, title, query_base, period: str = None):
        final_query = query_base
        if period:
            if "Data_criacao" in query_base:
                 date_range_sql = _get_date_range_sql(period)
            elif "Data_fim_execucao" in query_base: 
                 date_range_sql = _get_date_range_sql(period).replace('Data_criacao', 'Data_fim_execucao') 
            else: 
                 date_range_sql = _get_date_range_sql(period)

            if "WHERE" in final_query.upper():
                final_query += f" AND {date_range_sql}"
            else:
                final_query += f" WHERE {date_range_sql}"

        try:
            count_result = executar_query(final_query, return_type='one')
            count = count_result[0] if count_result and count_result[0] is not None else 0
        except Exception as e:
            print(f"Erro ao obter dados para card '{title}': {e}")
            count = "Erro"

        card_title_display = f"{title}"


        return ft.Card(
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.Text(card_title_display, size=24, weight="bold", color=ft.colors.BLACK),
                        ft.Text(str(count), size=26, weight="bold", color=ft.colors.GREEN_800),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=5
                ),
                width=280,
                height=150,
                bgcolor=ft.colors.GREEN_50,
                border_radius=10,
                border=ft.border.all(1, ft.colors.GREY_300), 
                alignment=ft.alignment.center,
                padding=15
            )
        )

    def create_disponibilidade_card(self, period: str):
        mtbf = calcular_mtbf_equipamento(period)
        
        mttr = self.average_time_card.data if hasattr(self.average_time_card, 'data') else 0.0

        disponibilidade_valor = 0.0
        if mtbf > 0 and mttr >= 0 and (mtbf + mttr) > 0:
            disponibilidade_valor = 100 * (mtbf / (mtbf + mttr))
        elif mtbf > 0 and mttr == 0:
            disponibilidade_valor = 100.0

        disponibilidade_display = f"{disponibilidade_valor:.2f}%"

        return ft.Card(
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.Text(f"Disponibilidade", size=24, weight="bold", color=ft.colors.BLACK),
                        ft.Text(disponibilidade_display, size=26, weight="bold", color=ft.colors.PURPLE_800),
                        ft.Text(f"Baseado em MTBF e MTTR", size=12, color=ft.colors.GREY_600)
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=5
                ),
                width=280,
                height=150,
                bgcolor=ft.colors.PURPLE_50,
                border_radius=10,
                border=ft.border.all(1, ft.colors.GREY_300), 
                alignment=ft.alignment.center,
                padding=15
            )
        )

    def create_top_equipment_chart_card(self, period: str):
        top_equipments_data = buscar_top_equipamentos_com_ordens(limit=5, period=period) 
        
        bar_groups = []
        bar_colors = [
            ft.colors.BLUE_500, ft.colors.GREEN_500, ft.colors.ORANGE_500, 
            ft.colors.RED_500, ft.colors.PURPLE_500
        ]
        
        if not top_equipments_data:
            return ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Text("Equipamentos com Mais Ordens", size=22, weight="bold"),
                        ft.Text("Sem dados de ordens no período selecionado.", size=14, color=ft.colors.GREY_600), 
                    ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    width=self.GRAPH_CARD_WIDTH, height=self.GRAPH_CARD_HEIGHT, bgcolor=ft.colors.GREY_100, border_radius=10, 
                    border=ft.border.all(1, ft.colors.GREY_300),
                    alignment=ft.alignment.center
                )
            )

        max_ordens = max([data[1] for data in top_equipments_data]) if top_equipments_data else 1
        y_values_interval = max(1, max_ordens // 5) 

        for i, (equipamento_nome, total_ordens) in enumerate(top_equipments_data):
            bar_groups.append(
                ft.BarChartGroup( 
                    x=i, 
                    bar_rods=[
                        ft.BarChartRod( 
                            from_y=0, 
                            to_y=total_ordens, 
                            width=15, 
                            color=bar_colors[i % len(bar_colors)], 
                            border_radius=3,
                            tooltip=f"{equipamento_nome}: {total_ordens} ordens", 
                        )
                    ]
                )
            )
        
        chart_width_internal = self.GRAPH_CARD_WIDTH - 50 
        chart_height_internal = self.GRAPH_CARD_HEIGHT - 100 

        chart = ft.BarChart( 
            bar_groups=bar_groups,
            border=ft.border.all(1, ft.colors.GREY_300),
            vertical_grid_lines=ft.ChartGridLines(interval=1, color=ft.colors.GREY_200, width=1), 
            horizontal_grid_lines=ft.ChartGridLines(interval=max(1, max_ordens // y_values_interval), color=ft.colors.GREY_200, width=1), 
            height=chart_height_internal, 
            width=chart_width_internal,  
            interactive=True, 
        )

        chart.min_x = -0.5 
        chart.max_x = len(top_equipments_data) - 0.5 
        chart.min_y = 0
        chart.max_y = max_ordens + (max_ordens * 0.1) 

        chart.bottom_axis = ft.ChartAxis( 
            title=ft.Text("Equipamentos"),
            labels=[
                ft.ChartAxisLabel( 
                    value=i,
                    label=ft.Container(
                        ft.Text(equipamento_nome, size=10, overflow=ft.TextOverflow.ELLIPSIS, max_lines=1), 
                        alignment=ft.alignment.center, 
                    ),
                )
                for i, (equipamento_nome, _) in enumerate(top_equipments_data)
            ],
            show_labels=True,
        )
        chart.vertical_axis = ft.ChartAxis( 
            title=ft.Text("Nº de Ordens"), 
            labels_interval=max(1, max_ordens // y_values_interval),
            labels=[ft.ChartAxisLabel(value=y, label=ft.Text(str(int(y)))) for y in range(0, max_ordens + max(1, max_ordens // y_values_interval), max(1, max_ordens // y_values_interval))], 
            show_labels=True,
        )

        return ft.Card(
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.Text("Equipamentos com Mais Ordens", size=22, weight=ft.FontWeight.BOLD, color=ft.colors.BLACK),
                        ft.Container(height=10), 
                        chart, 
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                width=self.GRAPH_CARD_WIDTH, 
                height=self.GRAPH_CARD_HEIGHT, 
                bgcolor=ft.colors.WHITE,
                border_radius=10,
                border=ft.border.all(1, ft.colors.GREY_300),
                alignment=ft.alignment.center,
                padding=15
            )
        )

    def create_orders_by_team_chart_card(self, period: str):
        orders_by_team_data = buscar_ordens_por_equipe(limit=5, period=period) 
        
        bar_groups = []
        bar_colors = [
            ft.colors.DEEP_PURPLE_500, ft.colors.TEAL_500, ft.colors.CYAN_500, 
            ft.colors.LIME_500, ft.colors.BROWN_500
        ]
        
        if not orders_by_team_data:
            return ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Text("Ordens por Equipe", size=22, weight="bold"),
                        ft.Text("Sem dados de ordens no período selecionado.", size=14, color=ft.colors.GREY_600), 
                    ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    width=self.GRAPH_CARD_WIDTH, height=self.GRAPH_CARD_HEIGHT, bgcolor=ft.colors.GREY_100, border_radius=10, 
                    border=ft.border.all(1, ft.colors.GREY_300),
                    alignment=ft.alignment.center
                )
            )

        max_ordens = max([data[1] for data in orders_by_team_data]) if orders_by_team_data else 1
        y_values_interval = max(1, max_ordens // 5) 

        for i, (equipe_nome, total_ordens) in enumerate(orders_by_team_data):
            bar_groups.append(
                ft.BarChartGroup(
                    x=i,
                    bar_rods=[
                        ft.BarChartRod(
                            from_y=0,
                            to_y=total_ordens,
                            width=15,
                            color=bar_colors[i % len(bar_colors)],
                            border_radius=3,
                            tooltip=f"Equipe {equipe_nome}: {total_ordens} ordens",
                        )
                    ]
                )
            )

        chart_width_internal = self.GRAPH_CARD_WIDTH - 50 
        chart_height_internal = self.GRAPH_CARD_HEIGHT - 100 

        chart = ft.BarChart( 
            bar_groups=bar_groups,
            border=ft.border.all(1, ft.colors.GREY_300),
            vertical_grid_lines=ft.ChartGridLines(interval=1, color=ft.colors.GREY_200, width=1), 
            horizontal_grid_lines=ft.ChartGridLines(interval=max(1, max_ordens // y_values_interval), color=ft.colors.GREY_200, width=1), 
            height=chart_height_internal, 
            width=chart_width_internal, 
            interactive=True, 
        )

        chart.min_x = -0.5
        chart.max_x = len(orders_by_team_data) - 0.5 
        chart.min_y = 0
        chart.max_y = max_ordens + (max_ordens * 0.1) 

        chart.bottom_axis = ft.ChartAxis( 
            title=ft.Text("Equipes"),
            labels=[
                ft.ChartAxisLabel( 
                    value=i,
                    label=ft.Container(
                        ft.Text(equipe_nome, size=10, overflow=ft.TextOverflow.ELLIPSIS, max_lines=1), 
                        alignment=ft.alignment.center,
                    ),
                )
                for i, (equipe_nome, _) in enumerate(orders_by_team_data)
            ],
            show_labels=True,
        )
        chart.vertical_axis = ft.ChartAxis( 
            title=ft.Text("Nº de Ordens"),
            labels_interval=max(1, max_ordens // y_values_interval),
            labels=[ft.ChartAxisLabel(value=y, label=ft.Text(str(int(y)))) for y in range(0, max_ordens + max(1, max_ordens // y_values_interval), max(1, max_ordens // y_values_interval))],
            show_labels=True,
        )

        return ft.Card(
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.Text("Ordens por Equipe", size=22, weight=ft.FontWeight.BOLD, color=ft.colors.BLACK),
                        ft.Container(height=10), 
                        chart, 
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                width=self.GRAPH_CARD_WIDTH, 
                height=self.GRAPH_CARD_HEIGHT, 
                bgcolor=ft.colors.WHITE,
                border_radius=10,
                border=ft.border.all(1, ft.colors.GREY_300),
                alignment=ft.alignment.center,
                padding=15
            )
        )

    def create_orders_by_classification_chart_card(self, period: str): 
        orders_by_classification_data = buscar_ordens_por_classificacao(period=period) 

        bar_groups = []
        bar_colors = { 
            "Preventiva": ft.colors.BLUE_700,
            "Corretiva": ft.colors.RED_700,
            "Preditiva": ft.colors.GREEN_700,
            "Melhoria": ft.colors.PURPLE_700,
            "Outro": ft.colors.GREY_500 
        }
        
        if not orders_by_classification_data:
            print("DEBUG: orders_by_classification_data está vazia ou nula.") 
            return ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Text("Classificação de Manutenção", size=22, weight="bold"),
                        ft.Text("Sem dados de ordens no período selecionado.", size=14, color=ft.colors.GREY_600), 
                    ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    width=self.GRAPH_CARD_WIDTH, height=self.GRAPH_CARD_HEIGHT, bgcolor=ft.colors.GREY_100, border_radius=10, 
                    border=ft.border.all(1, ft.colors.GREY_300),
                    alignment=ft.alignment.center
                )
            )
        
        print(f"DEBUG: orders_by_classification_data: {orders_by_classification_data}") 

        classifications_ordered = [
            "Preventiva", "Corretiva", "Preditiva", "Melhoria"
        ]
        data_map = {classification: 0 for classification in classifications_ordered}
        for classification_name, total_ordens in orders_by_classification_data:
            if classification_name in data_map: 
                data_map[classification_name] = total_ordens
            else:
                print(f"DEBUG: Classificação desconhecida encontrada: {classification_name}") 

        print(f"DEBUG: data_map para Classificação: {data_map}") 

        max_ordens = max(list(data_map.values())) if data_map.values() else 1 
        y_values_interval = max(1, max_ordens // 5) 

        for i, classification_name in enumerate(classifications_ordered):
            total_ordens = data_map[classification_name]
            bar_groups.append(
                ft.BarChartGroup(
                    x=i,
                    bar_rods=[
                        ft.BarChartRod(
                            from_y=0,
                            to_y=total_ordens,
                            width=15,
                            color=bar_colors.get(classification_name, bar_colors["Outro"]), 
                            border_radius=3,
                            tooltip=f"{classification_name}: {total_ordens} ordens",
                        )
                    ]
                )
            )
        
        chart_width_internal = self.GRAPH_CARD_WIDTH - 50 
        chart_height_internal = self.GRAPH_CARD_HEIGHT - 100 

        chart = ft.BarChart( 
            bar_groups=bar_groups,
            border=ft.border.all(1, ft.colors.GREY_300),
            vertical_grid_lines=ft.ChartGridLines(interval=1, color=ft.colors.GREY_200, width=1), 
            horizontal_grid_lines=ft.ChartGridLines(interval=max(1, max_ordens // y_values_interval), color=ft.colors.GREY_200, width=1), 
            height=chart_height_internal, 
            width=chart_width_internal, 
            interactive=True, 
        )

        chart.min_x = -0.5
        chart.max_x = len(classifications_ordered) - 0.5
        chart.min_y = 0
        chart.max_y = max_ordens + (max_ordens * 0.1) 

        chart.bottom_axis = ft.ChartAxis( 
            title=ft.Text("Classificação"), 
            labels=[
                ft.ChartAxisLabel( 
                    value=i,
                    label=ft.Container(
                        ft.Text(classification_name, size=10, overflow=ft.TextOverflow.ELLIPSIS, max_lines=1), 
                        alignment=ft.alignment.center,
                    ),
                )
                for i, classification_name in enumerate(classifications_ordered) 
            ],
            show_labels=True,
        )
        chart.vertical_axis = ft.ChartAxis( 
            title=ft.Text("Nº de Ordens"), 
            labels_interval=max(1, max_ordens // y_values_interval),
            labels=[ft.ChartAxisLabel(value=y, label=ft.Text(str(int(y)))) for y in range(0, max_ordens + max(1, max_ordens // y_values_interval), max(1, max_ordens // y_values_interval))], 
            show_labels=True,
        )

        return ft.Card(
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.Text("Classificação de Manutenção", size=22, weight=ft.FontWeight.BOLD, color=ft.colors.BLACK),
                        ft.Container(height=10), 
                        chart, 
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                width=self.GRAPH_CARD_WIDTH, 
                height=self.GRAPH_CARD_HEIGHT, 
                bgcolor=ft.colors.WHITE,
                border_radius=10,
                border=ft.border.all(1, ft.colors.GREY_300),
                alignment=ft.alignment.center,
                padding=15
            )
        )

    def create_cost_by_date_chart_card(self, period: str):
        cost_by_date_data = buscar_custo_por_data(period=period) 

        bar_groups = []
        bar_colors = [
            ft.colors.BLUE_GREY_700, ft.colors.DEEP_ORANGE_700, ft.colors.LIGHT_GREEN_700, 
            ft.colors.INDIGO_700, ft.colors.BROWN_700, ft.colors.CYAN_700, ft.colors.LIME_700
        ] 

        if not cost_by_date_data:
            print("DEBUG: cost_by_date_data está vazia ou nula.") 
            return ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Text("Custo Total por Data", size=22, weight="bold"),
                        ft.Text("Sem dados de custo no período selecionado.", size=14, color=ft.colors.GREY_600), 
                    ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    width=self.GRAPH_CARD_WIDTH, height=self.GRAPH_CARD_HEIGHT, bgcolor=ft.colors.GREY_100, border_radius=10, 
                    border=ft.border.all(1, ft.colors.GREY_300),
                    alignment=ft.alignment.center
                )
            )
        
        print(f"DEBUG: cost_by_date_data: {cost_by_date_data}") 

        labels_x_axis = []
        data_map = {}
        
        if period in ["last_week", "last_month"]:
            end_dt = datetime.now().date()
            if period == "last_week":
                start_dt = end_dt - timedelta(days=6)
            else: 
                start_dt = end_dt - timedelta(days=29)
            
            current_dt = start_dt
            while current_dt <= end_dt:
                labels_x_axis.append(current_dt.strftime("%d/%m"))
                data_map[current_dt.strftime("%Y-%m-%d")] = 0.0 
                current_dt += timedelta(days=1)
            
            for date_str, total_cost in cost_by_date_data:
                parsed_date = datetime.strptime(date_str, "%Y-%m-%d").strftime("%d/%m")
                if parsed_date in labels_x_axis:
                    data_map[date_str] = total_cost 
            
            bar_groups_temp = []
            for i, label_key in enumerate(labels_x_axis):
                real_date_key = (start_dt + timedelta(days=i)).strftime("%Y-%m-%d")
                cost_for_day = data_map.get(real_date_key, 0.0)
                
                bar_groups_temp.append(
                    ft.BarChartGroup(
                        x=i,
                        bar_rods=[
                            ft.BarChartRod(
                                from_y=0,
                                to_y=cost_for_day,
                                width=15,
                                color=bar_colors[i % len(bar_colors)],
                                border_radius=3,
                                tooltip=f"Custo em {label_key}: R$ {cost_for_day:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
                            )
                        ]
                    )
                )
            bar_groups = bar_groups_temp

        else: 
            end_dt = datetime.now().date()
            if period == "last_6_months":
                start_dt = end_dt - timedelta(days=180)
            else: 
                start_dt = end_dt - timedelta(days=365)
            
            current_month_dt = datetime(start_dt.year, start_dt.month, 1).date()
            while current_month_dt <= end_dt:
                labels_x_axis.append(current_month_dt.strftime("%Y-%m"))
                data_map[current_month_dt.strftime("%Y-%m")] = 0.0
                if current_month_dt.month == 12:
                    current_month_dt = datetime(current_month_dt.year + 1, 1, 1).date()
                else:
                    current_month_dt = datetime(current_month_dt.year, current_month_dt.month + 1, 1).date()
            
            for date_str, total_cost in cost_by_date_data:
                if date_str in labels_x_axis: 
                    data_map[date_str] = total_cost 
            
            bar_groups_temp = []
            for i, month_label in enumerate(labels_x_axis):
                cost_for_month = data_map.get(month_label, 0.0)
                bar_groups_temp.append(
                    ft.BarChartGroup(
                        x=i,
                        bar_rods=[
                            ft.BarChartRod(
                                from_y=0,
                                to_y=cost_for_month,
                                width=15,
                                color=bar_colors[i % len(bar_colors)],
                                border_radius=3,
                                tooltip=f"Custo em {month_label}: R$ {cost_for_month:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
                            )
                        ]
                    )
                )
            bar_groups = bar_groups_temp

        print(f"DEBUG: Labels X: {labels_x_axis}")
        print(f"DEBUG: Data Map para Custo por Data: {data_map}")
        
        max_cost = max(list(data_map.values())) if data_map.values() else 1.0
        y_values_interval = max(1.0, max_cost / 5) 

        chart_width_internal = self.GRAPH_CARD_WIDTH + 550
        chart_height_internal = self.GRAPH_CARD_HEIGHT - 100 

        chart = ft.BarChart( 
            bar_groups=bar_groups,
            border=ft.border.all(1, ft.colors.GREY_300),
            vertical_grid_lines=ft.ChartGridLines(interval=1, color=ft.colors.GREY_200, width=1), 
            horizontal_grid_lines=ft.ChartGridLines(interval=max(1.0, y_values_interval), color=ft.colors.GREY_200, width=1), 
            height=chart_height_internal, 
            width=chart_width_internal, 
            interactive=True, 
        )

        chart.min_x = -0.5
        chart.max_x = len(labels_x_axis) - 0.5 
        chart.min_y = 0.0 
        chart.max_y = max_cost + (max_cost * 0.1) 

        chart.bottom_axis = ft.ChartAxis( 
            title=ft.Text("Data"), 
            labels=[
                ft.ChartAxisLabel( 
                    value=i,
                    label=ft.Container(
                        ft.Text(label_x, size=10, overflow=ft.TextOverflow.ELLIPSIS, max_lines=1), 
                        alignment=ft.alignment.center,
                    ),
                )
                for i, label_x in enumerate(labels_x_axis) 
            ],
            show_labels=True,
        )
        chart.vertical_axis = ft.ChartAxis( 
            title=ft.Text("Custo Total (R$)"), 
            labels_interval=max(1.0, y_values_interval),
            labels=[ft.ChartAxisLabel(value=y, label=ft.Text(f"R$ {y:,.0f}".replace(",", "X").replace(".", ",").replace("X", "."))) for y in range(0, int(max_cost + (max_cost * 0.1)) + 1, int(max(1.0, y_values_interval)))], 
            show_labels=True,
        )

        return ft.Card(
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.Text("Custo Total por Data", size=22, weight=ft.FontWeight.BOLD, color=ft.colors.BLACK),
                        ft.Container(height=10), 
                        chart, 
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                width=self.GRAPH_CARD_WIDTH + 600, 
                height=self.GRAPH_CARD_HEIGHT, 
                bgcolor=ft.colors.WHITE,
                border_radius=10,
                border=ft.border.all(1, ft.colors.GREY_300),
                alignment=ft.alignment.center,
                padding=15
            )
        )

def tela_dashboard(page: ft.Page):
    return DashboardView(page)