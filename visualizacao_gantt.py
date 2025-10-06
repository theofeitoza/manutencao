import flet as ft
from datetime import datetime, timedelta, date
from db_utils import executar_query

MIN_PIXELS_POR_DIA = 5
MAX_DAYS_IN_VIEW = 90

class GanttView(ft.Column):
    def __init__(self, page: ft.Page):
        super().__init__(expand=True, scroll=ft.ScrollMode.ADAPTIVE, spacing=5)
        self.page = page

        self.all_tasks = self.carregar_dados_ordens()
        self.apply_colors_to_tasks()

        self.start_display_date = date.today()
        self.end_display_date = date.today() + timedelta(days=30)

        self.gantt_chart_container = ft.Column(spacing=5, scroll=ft.ScrollMode.ADAPTIVE, expand=True)
        self.header_row_container = ft.Row(spacing=0)
        self.start_date_text = ft.Text(f"Início: {self.start_display_date.strftime('%d/%m/%Y')}")
        self.end_date_text = ft.Text(f"Fim: {self.end_display_date.strftime('%d/%m/%Y')}")

        self.date_picker_start = ft.DatePicker(
            first_date=datetime(2023, 1, 1),
            last_date=datetime(2026, 12, 31),
            on_change=self.on_start_date_change,
            value=datetime(self.start_display_date.year, self.start_display_date.month, self.start_display_date.day)
        )
        self.page.overlay.append(self.date_picker_start)

        self.date_picker_end = ft.DatePicker(
            first_date=datetime(2023, 1, 1),
            last_date=datetime(2026, 12, 31),
            on_change=self.on_end_date_change,
            value=datetime(self.end_display_date.year, self.end_display_date.month, self.end_display_date.day)
        )
        self.page.overlay.append(self.date_picker_end)

        self.page.snack_bar = ft.SnackBar(ft.Text(""), open=False)
        self.page.add(self.page.snack_bar)

        self.controls = [
            ft.Text("Diagrama de Gantt das Ordens", size=24, weight=ft.FontWeight.BOLD),
            ft.Divider(),
            ft.Row(
                [
                    ft.ElevatedButton(
                        "Selecionar Data de Início",
                        icon=ft.icons.CALENDAR_MONTH,
                        on_click=lambda _: self.date_picker_start.pick_date(),
                    ),
                    self.start_date_text,
                    ft.VerticalDivider(),
                    ft.ElevatedButton(
                        "Selecionar Data Final",
                        icon=ft.icons.CALENDAR_MONTH,
                        on_click=lambda _: self.date_picker_end.pick_date(),
                    ),
                    self.end_date_text,
                ],
                alignment=ft.MainAxisAlignment.CENTER
            ),
            self.header_row_container,
            self.gantt_chart_container
        ]

        self.update_gantt_chart()

    def carregar_dados_ordens(self):
        query = "SELECT Id, Status, Data_inicio_execucao, Data_fim_execucao FROM ordens ORDER BY Data_inicio_execucao ASC"
        resultados = executar_query(query)

        tarefas = []
        for id_ordem, status, inicio, fim in resultados:
            try:
                if not inicio or not fim:
                    continue

                inicio_fmt = datetime.strptime(inicio.split(" ")[0], "%Y-%m-%d").date()
                fim_fmt = datetime.strptime(fim.split(" ")[0], "%Y-%m-%d").date()

                if inicio_fmt > fim_fmt:
                    inicio_fmt = fim_fmt

                duracao_dias = (fim_fmt - inicio_fmt).days + 1
                tarefas.append({
                    "name": f"OS: {id_ordem}", 
                    "status": status,
                    "start": inicio_fmt, 
                    "end": fim_fmt,
                    "progress": 100 if status == "Encerrada" else 0,
                    "duration": duracao_dias, 
                    "color": None
                })
            except Exception as e:
                print(f"Erro ao processar ordem '{id_ordem}': {e}")
                pass
        return tarefas

    def get_days_between(self, start_date, end_date):
        return (end_date - start_date).days + 1

    def _get_color_from_due_date_proximity(self, task_end_date: date):
        today = date.today()
        days_diff = (task_end_date - today).days

        COLOR_RED = (255, 0, 0)
        COLOR_YELLOW = (255, 255, 0)
        COLOR_GREEN = (0, 255, 0)

        point1_days = 0
        point2_days = 15
        point3_days = 30

        if days_diff <= point1_days:
            red, green, blue = COLOR_RED
        elif days_diff <= point2_days:
            norm = (days_diff - point1_days) / (point2_days - point1_days)
            red = int(COLOR_RED[0] + (COLOR_YELLOW[0] - COLOR_RED[0]) * norm)
            green = int(COLOR_RED[1] + (COLOR_YELLOW[1] - COLOR_RED[1]) * norm)
            blue = int(COLOR_RED[2] + (COLOR_YELLOW[2] - COLOR_RED[2]) * norm)
        elif days_diff <= point3_days:
            norm = (days_diff - point2_days) / (point3_days - point2_days)
            red = int(COLOR_YELLOW[0] + (COLOR_GREEN[0] - COLOR_YELLOW[0]) * norm)
            green = int(COLOR_YELLOW[1] + (COLOR_GREEN[1] - COLOR_YELLOW[1]) * norm)
            blue = int(COLOR_YELLOW[2] + (COLOR_GREEN[2] - COLOR_YELLOW[2]) * norm)
        else:
            red, green, blue = COLOR_GREEN

        return f"#{red:02x}{green:02x}{blue:02x}"

    def apply_colors_to_tasks(self):
        """Aplica a lógica de cores a todas as tarefas."""
        for task in self.all_tasks:
            if task["status"] == "Encerrada":
                task["color"] = ft.colors.BLUE_700
            else:
                task["color"] = self._get_color_from_due_date_proximity(task["end"])

    def create_gantt_bar(self, task, view_start_date, view_end_date, calculated_pixels_per_day):
        visible_start_date = max(task["start"], view_start_date)
        visible_end_date = min(task["end"], view_end_date)
        if visible_start_date > visible_end_date:
            return ft.Container(width=0, height=0)
        
        start_offset_days = (visible_start_date - view_start_date).days
        padding_left = start_offset_days * calculated_pixels_per_day
        
        visible_duration_days = self.get_days_between(visible_start_date, visible_end_date)
        bar_width = visible_duration_days * calculated_pixels_per_day
        
        progress_bar_width = bar_width if task["progress"] == 100 else 0

        return ft.Container(
            content=ft.Stack(
                [
                    ft.Container(width=bar_width, height=20, bgcolor=task["color"], border_radius=ft.border_radius.all(5), opacity=0.7),
                    ft.Container(width=progress_bar_width, height=20, bgcolor=ft.colors.with_opacity(0.4, ft.colors.BLACK), border_radius=ft.border_radius.all(5)),
                ]
            ),
            padding=ft.padding.only(left=padding_left),
            alignment=ft.alignment.center_left,
            height=30,
        )

    def show_message(self, message, color=ft.colors.RED_ACCENT_700):
        if not hasattr(self.page, 'snack_bar'):
             self.page.snack_bar = ft.SnackBar(ft.Text(""), open=False)
             self.page.overlay.append(self.page.snack_bar)

        self.page.snack_bar.content = ft.Text(message)
        self.page.snack_bar.bgcolor = color
        self.page.snack_bar.open = True
        self.page.update()

    def update_gantt_chart(self):
        self.apply_colors_to_tasks()

        total_view_days = self.get_days_between(self.start_display_date, self.end_display_date)
        if total_view_days <= 0:
            return

        task_name_column_width = 200
        padding_for_spacing = 20
        available_width = self.page.window.width - task_name_column_width - padding_for_spacing
        calculated_pixels_per_day = max(MIN_PIXELS_POR_DIA, available_width / total_view_days)

        filtered_tasks = [
            t for t in self.all_tasks
            if (t["start"] <= self.end_display_date and t["end"] >= self.start_display_date)
        ]

        self.gantt_chart_container.controls.clear()
        self.header_row_container.controls.clear()

        date_headers = []
        current_date = self.start_display_date
        while current_date <= self.end_display_date:
            date_headers.append(
                ft.Container(
                    content=ft.Text(value=current_date.strftime("%d/%m"), size=10, weight=ft.FontWeight.BOLD),
                    width=calculated_pixels_per_day,
                    alignment=ft.alignment.center,
                    padding=ft.padding.symmetric(vertical=5, horizontal=max(0, (calculated_pixels_per_day - 20) / 2))
                )
            )
            current_date += timedelta(days=1)

        self.header_row_container.controls.extend([
            ft.Container(content=ft.Text("Ordem (ID)", weight=ft.FontWeight.BOLD), width=task_name_column_width, alignment=ft.alignment.center_left),
            ft.Row(date_headers, spacing=0)
        ])

        for task in filtered_tasks:
            gantt_chart_rows_controls = ft.Row(
                [
                    ft.Container(
                        content=ft.Text(task["name"]),
                        width=task_name_column_width,
                        alignment=ft.alignment.center_left,
                        padding=ft.padding.only(left=10)
                    ),
                    ft.Container(
                        content=self.create_gantt_bar(task, self.start_display_date, self.end_display_date, calculated_pixels_per_day),
                        expand=True
                    )
                ],
                spacing=0,
                vertical_alignment=ft.CrossAxisAlignment.CENTER
            )
            self.gantt_chart_container.controls.append(gantt_chart_rows_controls)

        self.start_date_text.value = f"Início: {self.start_display_date.strftime('%d/%m/%Y')}"
        self.end_date_text.value = f"Fim: {self.end_display_date.strftime('%d/%m/%Y')}"

        self.page.update()

    def on_start_date_change(self, e):
        if self.date_picker_start.value:
            new_start_date = self.date_picker_start.value.date()
            if (self.end_display_date - new_start_date).days > MAX_DAYS_IN_VIEW - 1:
                self.end_display_date = new_start_date + timedelta(days=MAX_DAYS_IN_VIEW - 1)
                self.show_message(f"Período limitado a {MAX_DAYS_IN_VIEW} dias. Data final ajustada.", ft.colors.AMBER_700)
            self.start_display_date = new_start_date
            self.update_gantt_chart()

    def on_end_date_change(self, e):
        if self.date_picker_end.value:
            new_end_date = self.date_picker_end.value.date()
            if (new_end_date - self.start_display_date).days > MAX_DAYS_IN_VIEW - 1:
                self.start_display_date = new_end_date - timedelta(days=MAX_DAYS_IN_VIEW - 1)
                self.show_message(f"Período limitado a {MAX_DAYS_IN_VIEW} dias. Data de início ajustada.", ft.colors.AMBER_700)
            self.end_display_date = new_end_date
            self.update_gantt_chart()

def tela_gantt(page: ft.Page):
    return GanttView(page)