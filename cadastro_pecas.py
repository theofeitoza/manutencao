import flet as ft
from databases import salvar_pecas, buscar_nomes_pecas, buscar_dados_peca, atualizar_peca

def criar_dialogo_pecas(page: ft.Page, atualizar_tabela_callback):
    nome_peca_ref = ft.Ref[ft.TextField]()
    descricao_peca_ref = ft.Ref[ft.TextField]()
    fabricante_ref = ft.Ref[ft.TextField]()
    dimensoes_ref = ft.Ref[ft.TextField]()
    peso_ref = ft.Ref[ft.TextField]()
    quantidade_ref = ft.Ref[ft.TextField]()
    custo_unitario_ref = ft.Ref[ft.TextField]()
    classe_ref = ft.Ref[ft.RadioGroup]()
    cadastro_dialog_ref = ft.Ref[ft.AlertDialog]()

    def cadastrar_peca(e):
        nome_peca_ref.current.error_text = None
        descricao_peca_ref.current.error_text = None
        fabricante_ref.current.error_text = None
        dimensoes_ref.current.error_text = None
        peso_ref.current.error_text = None
        quantidade_ref.current.error_text = None
        custo_unitario_ref.current.error_text = None

        nome_peca = nome_peca_ref.current.value.strip() if nome_peca_ref.current.value else ""
        descricao_peca = descricao_peca_ref.current.value.strip() if descricao_peca_ref.current.value else ""
        fabricante = fabricante_ref.current.value.strip() if fabricante_ref.current.value else ""
        dimensoes = dimensoes_ref.current.value.strip() if dimensoes_ref.current.value else ""
        classe = classe_ref.current.value
        custo_unitario_str = custo_unitario_ref.current.value.strip().replace(',', '.') if custo_unitario_ref.current.value else ""
        
        erros = []

        if not nome_peca:
            erros.append("O campo 'Nome da Peça' é obrigatório.")
            nome_peca_ref.current.error_text = "Preenchimento obrigatório"
        if not descricao_peca:
            erros.append("O campo 'Descrição da Peça' é obrigatório.")
            descricao_peca_ref.current.error_text = "Preenchimento obrigatório"
        if not fabricante:
            erros.append("O campo 'Fabricante' é obrigatório.")
            fabricante_ref.current.error_text = "Preenchimento obrigatório"
        if not dimensoes:
            erros.append("O campo 'Dimensões' é obrigatório.")
            dimensoes_ref.current.error_text = "Preenchimento obrigatório"

        peso = None
        if peso_ref.current.value.strip():
            try:
                peso = float(peso_ref.current.value.strip().replace(',', '.'))
            except ValueError:
                erros.append("O campo 'Peso' deve ser um número válido.")
                peso_ref.current.error_text = "Insira um número válido (ex: 1.5)"
        else:
            erros.append("O campo 'Peso' é obrigatório.")
            peso_ref.current.error_text = "Preenchimento obrigatório"

        quantidade = None
        if quantidade_ref.current.value.strip():
            try:
                quantidade = int(quantidade_ref.current.value.strip())
                if quantidade < 0:
                    erros.append("A 'Quantidade' deve ser um número não-negativo.")
                    quantidade_ref.current.error_text = "Insira uma quantidade válida (>= 0)."
            except ValueError:
                erros.append("O campo 'Quantidade' deve ser um número inteiro.")
                quantidade_ref.current.error_text = "Insira um número inteiro válido (ex: 10)."
        else:
            erros.append("O campo 'Quantidade' é obrigatório.")
            quantidade_ref.current.error_text = "Preenchimento obrigatório"

        custo_unitario = None
        if custo_unitario_str:
            try:
                custo_unitario = float(custo_unitario_str)
                if custo_unitario < 0:
                    erros.append("O Custo Unitário não pode ser negativo.")
                    custo_unitario_ref.current.error_text = "Valor inválido"
            except ValueError:
                erros.append("O Custo Unitário deve ser um número válido.")
                custo_unitario_ref.current.error_text = "Número inválido (ex: 10.50)"
        else:
            erros.append("O campo 'Custo Unitário' é obrigatório.")
            custo_unitario_ref.current.error_text = "Preenchimento obrigatório"

        if not classe:
            erros.append("O campo 'Classe' é obrigatório.")
        
        page.update()

        if erros:
            page.dialog = ft.AlertDialog(
                title=ft.Text("Erro no Cadastro"),
                content=ft.Column([ft.Text(e) for e in erros], tight=True),
                actions=[ft.TextButton("Ok", on_click=lambda e: setattr(page.dialog, "open", False) or page.update())],
                modal=True
            )
            page.dialog.open = True
            page.update()
            return

        nomes_pecas = buscar_nomes_pecas()

        if nome_peca in nomes_pecas:
            dados_peca_existente = buscar_dados_peca(nome_peca)
            if dados_peca_existente:
                id_peca = dados_peca_existente['Id']
                atualizar_peca(id_peca, nome_peca, descricao_peca, fabricante, dimensoes, peso, quantidade, classe, custo_unitario)
                msg_sucesso = f"Peça '{nome_peca}' atualizada com sucesso!"
            else:
                erros.append("Erro interno: Peça existente não encontrada para atualização.")
                return
        else:
            salvar_pecas(nome_peca, descricao_peca, fabricante, dimensoes, peso, quantidade, classe, custo_unitario)
            msg_sucesso = f"Peça '{nome_peca}' cadastrada com sucesso!"
        
        cadastro_dialog_ref.current.open = False
        limpar_campos(None)
        atualizar_tabela_callback()
        page.snack_bar = ft.SnackBar(ft.Text(msg_sucesso), open=True)
        page.update()

    def limpar_campos(e):
        nome_peca_ref.current.value = ""
        descricao_peca_ref.current.value = ""
        fabricante_ref.current.value = ""
        dimensoes_ref.current.value = ""
        peso_ref.current.value = ""
        quantidade_ref.current.value = ""
        custo_unitario_ref.current.value = ""
        
        nome_peca_ref.current.error_text = None
        descricao_peca_ref.current.error_text = None
        fabricante_ref.current.error_text = None
        dimensoes_ref.current.error_text = None
        peso_ref.current.error_text = None
        quantidade_ref.current.error_text = None
        custo_unitario_ref.current.error_text = None
        classe_ref.current.value = None
        page.update()

    def fechar_dialogo(e):
        cadastro_dialog_ref.current.open = False
        page.update()

    cadastro_dialog = ft.AlertDialog(
        modal=True,
        content=ft.Column(
            [
                ft.Text("Cadastro de Peças", size=20, weight=ft.FontWeight.BOLD),
                ft.TextField(label="Nome da Peça", ref=nome_peca_ref),
                ft.TextField(label="Descrição da Peça", max_length=400, multiline=True, ref=descricao_peca_ref),
                ft.TextField(label="Fabricante", max_length=50, ref=fabricante_ref),
                ft.TextField(label="Dimensões", max_length=50, ref=dimensoes_ref),
                ft.TextField(label="Peso (Kg)", ref=peso_ref, keyboard_type=ft.KeyboardType.NUMBER),
                ft.TextField(label="Quantidade em Estoque", ref=quantidade_ref, keyboard_type=ft.KeyboardType.NUMBER),
                ft.TextField(
                    label="Custo Unitário (R$)", ref=custo_unitario_ref,
                    keyboard_type=ft.KeyboardType.NUMBER,
                    input_filter=ft.InputFilter(allow=True, regex_string=r"[0-9.,]")
                ),
                ft.RadioGroup(
                    ref=classe_ref,
                    content=ft.Column(
                        [
                            ft.Text("Classe"),
                            ft.Radio(value="Elétrico", label="Elétrico"),
                            ft.Radio(value="Mecânico", label="Mecânico"),
                            ft.Radio(value="Hidráulico", label="Hidráulico"),
                            ft.Radio(value="Eletrônico", label="Eletrônico"),
                        ],
                    ),
                ),
                ft.Row(
                    [
                        ft.ElevatedButton("Cadastrar", on_click=cadastrar_peca),
                        ft.ElevatedButton("Limpar", on_click=limpar_campos),
                        ft.ElevatedButton("Fechar", on_click=fechar_dialogo),
                    ], alignment=ft.MainAxisAlignment.SPACE_EVENLY),
            ],
            scroll=ft.ScrollMode.ADAPTIVE
        ),
        ref=cadastro_dialog_ref,
    )

    page.overlay.append(cadastro_dialog)

    def abrir_dialogo():
        limpar_campos(None)
        cadastro_dialog_ref.current.open = True
        page.update()

    return abrir_dialogo