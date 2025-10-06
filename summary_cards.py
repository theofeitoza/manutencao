import flet as ft
from db_utils import executar_query, _get_date_range_sql
from datetime import datetime, timedelta

def calcular_mtbf_equipamento(period: str):
    date_range_sql = _get_date_range_sql(period)

    query = f"""
        SELECT Equipamento, Horario_fechamento, Horario_abertura
        FROM ordens
        WHERE Status = 'Encerrada'
        AND Horario_fechamento IS NOT NULL
        AND Horario_abertura IS NOT NULL
        AND {date_range_sql}
        ORDER BY Equipamento, Horario_fechamento
    """
    ordens = executar_query(query)

    tempos_entre_falhas = {}
    ultima_data_fechamento_por_equipamento = {}

    for equipamento, fechamento_str, abertura_str in ordens:
        try:
            fechamento_dt = datetime.strptime(fechamento_str, "%Y-%m-%d %H:%M:%S")
            abertura_dt = datetime.strptime(abertura_str, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            continue

        if equipamento not in tempos_entre_falhas:
            tempos_entre_falhas[equipamento] = []

        if equipamento in ultima_data_fechamento_por_equipamento:
            diferenca_timedelta = abertura_dt - ultima_data_fechamento_por_equipamento[equipamento]
            diferenca_horas = diferenca_timedelta.total_seconds() / 3600.0
            if diferenca_horas > 0:
                tempos_entre_falhas[equipamento].append(diferenca_horas)

        ultima_data_fechamento_por_equipamento[equipamento] = fechamento_dt

    mtbf_por_equipamento = {}
    for equipamento, tempos in tempos_entre_falhas.items():
        if len(tempos) > 0:
            mtbf_por_equipamento[equipamento] = sum(tempos) / len(tempos)
        else:
            mtbf_por_equipamento[equipamento] = 0.0

    mtbfs_validos = [v for v in mtbf_por_equipamento.values() if v is not None and v > 0]
    media_geral_mtbf_horas = sum(mtbfs_validos) / len(mtbfs_validos) if mtbfs_validos else 0.0

    return media_geral_mtbf_horas

def criar_cartao_mtbf(period: str):
    media_geral_mtbf = calcular_mtbf_equipamento(period)

    conteudo_card = []
    conteudo_card.append(ft.Text("MTBF", size=24, weight="bold", color=ft.colors.BLACK)) 

    if media_geral_mtbf > 0:
        horas_inteiras_media = int(media_geral_mtbf)
        
        conteudo_card.append(
            ft.Text(
                f"{horas_inteiras_media}h",
                size=26,
                weight="bold",
                color=ft.colors.BLUE_800
            )
        )
        conteudo_card.append(ft.Text(f"Média entre falhas", size=14, color=ft.colors.GREY_600)) 
    else:
        conteudo_card.append(
            ft.Text("Sem dados no período selecionado", size=14, color=ft.colors.GREY_600)
        )

    return ft.Card(
        content=ft.Container(
            content=ft.Column(
                conteudo_card,
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
        )
    )

def criar_cartoes_resumo(titulo, tabela, mostrar_menores=False):
    linha_cartoes = ft.Row(
        alignment=ft.MainAxisAlignment.CENTER,
        spacing=20,
    )

    total_itens = executar_query(f"SELECT COUNT(*) FROM {tabela}", return_type='one')[0]

    linha_cartoes.controls.append(
        ft.Card(
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.Text(titulo, size=24, weight="bold", color=ft.colors.BLACK),
                        ft.Text(
                            f"{total_itens} itens",
                            size=16,
                            color=ft.colors.BLACK,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                width=280,
                height=150,
                bgcolor=ft.colors.GREY_50,
                border_radius=10,
                border=ft.border.all(1, ft.colors.GREY_300),
                alignment=ft.alignment.center,
                padding=15
            )
        )
    )

    if mostrar_menores:
        pecas_menor_quantidade = executar_query(
            f"SELECT nome_peca, quantidade FROM {tabela} ORDER BY quantidade ASC LIMIT 3"
        )

        for nome, quantidade in pecas_menor_quantidade:
            linha_cartoes.controls.append(
                ft.Card(
                    content=ft.Container(
                        content=ft.Column(
                            [
                                ft.Text(nome, size=18, weight="bold", color=ft.colors.BLACK),
                                ft.Text(
                                    f"Quantidade: {quantidade}",
                                    size=16,
                                    color=ft.colors.RED if quantidade < 50 else ft.colors.BLACK,
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.CENTER,
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                        width=280,
                        height=150,
                        bgcolor=ft.colors.GREY_50,
                        border_radius=10,
                        border=ft.border.all(1, ft.colors.GREY_300),
                        alignment=ft.alignment.center,
                        padding=15
                    )
                )
            )

    return ft.Container(
        content=linha_cartoes,
        alignment=ft.alignment.center
    )