from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from datetime import datetime
import os
import sqlite3

BANCO_DADOS_UNICO = "manutencao.db"


def obter_nomes_colunas(tabela):
    with sqlite3.connect(BANCO_DADOS_UNICO) as conn:
        cursor = conn.cursor()
        cursor.execute(f"PRAGMA table_info({tabela})")
        colunas = [info[1] for info in cursor.fetchall()]
    return colunas


def gerar_pdf_linha_dados(tabela: str, dados: tuple):
    colunas = obter_nomes_colunas(tabela)

    pasta_pdfs = os.path.join(os.getcwd(), "pdfs_gerados")
    os.makedirs(pasta_pdfs, exist_ok=True)

    nome_arquivo = f"linha_{tabela}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    caminho_arquivo = os.path.join(pasta_pdfs, nome_arquivo)

    doc = SimpleDocTemplate(caminho_arquivo, pagesize=A4,
                            rightMargin=40, leftMargin=40,
                            topMargin=60, bottomMargin=40)
    
    styles = getSampleStyleSheet()
    style_header = ParagraphStyle(name="header", fontSize=14, leading=18, spaceAfter=12, alignment=1, fontName="Helvetica-Bold")
    style_label = ParagraphStyle(name="label", fontSize=12, leading=15, fontName="Helvetica-Bold", textColor=colors.darkblue)
    style_value = ParagraphStyle(name="value", fontSize=12, leading=15)

    elementos = []

    titulo = Paragraph(f"Registro da Tabela: {tabela.capitalize()}", style_header)
    elementos.append(titulo)
    elementos.append(Spacer(1, 12))

    data = []
    for coluna, valor in zip(colunas, dados):
        data.append([
            Paragraph(coluna.capitalize(), style_label),
            Paragraph(str(valor) if valor is not None else '', style_value)
        ])

    tabela_pdf = Table(data, colWidths=[150, 350])
    
    estilo_tabela = TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.whitesmoke),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ])

    for i in range(len(data)):
        if i % 2 == 0:
            estilo_tabela.add('BACKGROUND', (0, i), (-1, i), colors.lightgrey)

    tabela_pdf.setStyle(estilo_tabela)

    elementos.append(tabela_pdf)

    def rodape(canvas, doc):
        canvas.saveState()
        texto_rodape = f"Gerado em {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"
        canvas.setFont('Helvetica-Oblique', 9)
        canvas.drawString(40, 20, texto_rodape)
        canvas.drawRightString(A4[0] - 40, 20, f"Página {doc.page}")
        canvas.restoreState()

    doc.build(elementos, onFirstPage=rodape, onLaterPages=rodape)

    print(f"PDF gerado com sucesso: {caminho_arquivo}")
