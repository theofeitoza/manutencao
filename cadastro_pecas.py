import flet as ft
from databases import salvar_pecas, buscar_nomes_pecas, buscar_dados_peca, atualizar_peca  # Ajuste o import se necessário

def criar_dialogo_pecas(page: ft.Page, atualizar_tabela_callback):
    # Referências para os campos
    nome_peca_dropdown_ref = ft.Ref[ft.Dropdown]()
    novo_nome_peca_ref = ft.Ref[ft.TextField]()
    descricao_peca_ref = ft.Ref[ft.TextField]()
    fabricante_ref = ft.Ref[ft.TextField]()
    dimensoes_ref = ft.Ref[ft.TextField]()
    peso_ref = ft.Ref[ft.TextField]()
    quantidade_ref = ft.Ref[ft.TextField]()  # Usando TextField para quantidade
    classe_ref = ft.Ref[ft.RadioGroup]()
    cadastro_dialog_ref = ft.Ref[ft.AlertDialog]()
    
    # Função para atualizar a visibilidade do campo "Novo Nome"
    def atualizar_visibilidade_novo_nome(e):
        if nome_peca_dropdown_ref.current.value == "Novo Nome":
            novo_nome_peca_ref.current.visible = True
        else:
            novo_nome_peca_ref.current.visible = False
        page.update()

    # Busca os nomes das peças existentes no banco
    nomes_pecas = buscar_nomes_pecas()

    # Função para preencher os campos com os dados da peça selecionada
    def preencher_campos_peca(e):
        nome_peca = nome_peca_dropdown_ref.current.value
        if nome_peca and nome_peca != "Novo Nome":
            # Buscar os dados da peça pelo nome
            dados_peca = buscar_dados_peca(nome_peca)
            if dados_peca:
                # Preencher os campos com os dados
                descricao_peca_ref.current.value = dados_peca['descricao']
                fabricante_ref.current.value = dados_peca['fabricante']
                dimensoes_ref.current.value = dados_peca['dimensoes']
                peso_ref.current.value = dados_peca['peso']
                quantidade_ref.current.value = str(dados_peca['quantidade'])
                classe_ref.current.value = dados_peca['classe']
                page.update()

    def cadastrar_peca(e):
        nome_peca = None
        if nome_peca_dropdown_ref.current.value is not None:
            nome_peca = (
                nome_peca_dropdown_ref.current.value.strip()
                if nome_peca_dropdown_ref.current.value != "Novo Nome"
                else novo_nome_peca_ref.current.value.strip() if novo_nome_peca_ref.current.value else None
            )

        descricao_peca = descricao_peca_ref.current.value.strip() if descricao_peca_ref.current.value else None
        fabricante = fabricante_ref.current.value.strip() if fabricante_ref.current.value else None
        dimensoes = dimensoes_ref.current.value.strip() if dimensoes_ref.current.value else None
        peso = float(peso_ref.current.value) if peso_ref.current.value else None
        classe = classe_ref.current.value
        quantidade = int(quantidade_ref.current.value) if quantidade_ref.current.value else None

        erros = []

        # Validações
        if not nome_peca:
            erros.append("O campo 'Nome da Peça' é obrigatório.")
            novo_nome_peca_ref.current.error_text = "Preenchimento obrigatório"
        else:
            novo_nome_peca_ref.current.error_text = None

        if not descricao_peca:
            erros.append("O campo 'Descrição da Peça' é obrigatório.")
            descricao_peca_ref.current.error_text = "Preenchimento obrigatório"
        else:
            descricao_peca_ref.current.error_text = None

        if not fabricante:
            erros.append("O campo 'Fabricante' é obrigatório.")
            fabricante_ref.current.error_text = "Preenchimento obrigatório"
        else:
            fabricante_ref.current.error_text = None

        if not dimensoes:
            erros.append("O campo 'Dimensões' é obrigatório.")
            dimensoes_ref.current.error_text = "Preenchimento obrigatório"
        else:
            dimensoes_ref.current.error_text = None

        if peso is None:
            erros.append("O campo 'Peso' é obrigatório.")
            peso_ref.current.error_text = "Preenchimento obrigatório"
        else:
            peso_ref.current.error_text = None

        if not quantidade or quantidade <= 0:
            erros.append("O campo 'Quantidade' deve ser um número inteiro positivo.")
            quantidade_ref.current.error_text = "Insira uma quantidade válida."
        else:
            quantidade_ref.current.error_text = None

        if not classe:
            erros.append("O campo 'Classe' é obrigatório.")

        page.update()

        # Se houver erros, exibir alerta
        if erros:
            page.dialog = ft.AlertDialog(
                title=ft.Text("Erro no Cadastro"),
                content=ft.Text("\n".join(erros)),
            )
            page.dialog.open = True
            return

        # Verificar se a peça já existe
        if nome_peca in nomes_pecas:
            # Atualizar peça existente
            atualizar_peca(nome_peca, descricao_peca, fabricante, dimensoes, peso, quantidade, classe)
            mensagem = f"Os dados da peça '{nome_peca}' foram atualizados com sucesso!"
        else:
            # Criar uma nova peça
            id_gerado = salvar_pecas(
                nome_peca, descricao_peca, fabricante, dimensoes, peso, quantidade, classe
            )
            mensagem = f"A peça foi cadastrada com sucesso! ID: {id_gerado}"

        # Exibir mensagem de sucesso
        page.dialog = ft.AlertDialog(
            title=ft.Text("Operação bem-sucedida"),
            content=ft.Text(mensagem),
        )
        page.dialog.open = True
        limpar_campos(e)
        page.update()


    # Função para limpar os campos
    def limpar_campos(e):
        nome_peca_dropdown_ref.current.value = None
        novo_nome_peca_ref.current.value = ""
        descricao_peca_ref.current.value = ""
        fabricante_ref.current.value = ""
        dimensoes_ref.current.value = ""
        peso_ref.current.value = ""
        quantidade_ref.current.value = ""
        descricao_peca_ref.current.error_text = None
        fabricante_ref.current.error_text = None
        dimensoes_ref.current.error_text = None
        peso_ref.current.error_text = None
        quantidade_ref.current.error_text = None
        classe_ref.current.value = None
        atualizar_visibilidade_novo_nome(e)
        page.update()

    atualizar_tabela_callback()

    # Função para fechar o diálogo
    def fechar_dialogo(e):
        cadastro_dialog_ref.current.open = False
        page.update()

    # Diálogo de cadastro
    cadastro_dialog = ft.AlertDialog(
        modal=True,
        content=ft.Column(
            [
                ft.Text("Cadastro de Peças", size=20, weight=ft.FontWeight.BOLD),
                ft.Dropdown(
                    label="Nome da Peça",
                    options=[ft.dropdown.Option("Novo Nome")] + [ft.dropdown.Option(n) for n in nomes_pecas],
                    ref=nome_peca_dropdown_ref,
                    on_change=lambda e: [atualizar_visibilidade_novo_nome(e), preencher_campos_peca(e)],  # Adicionando chamada à função de preenchimento
                ),
                ft.TextField(
                    label="Digite um novo nome",
                    ref=novo_nome_peca_ref,
                    visible=False,
                ),
                ft.TextField(label="Descrição da Peça", max_length=400, multiline=True, ref=descricao_peca_ref),
                ft.TextField(label="Fabricante", max_length=50, ref=fabricante_ref),
                ft.TextField(label="Dimensões", max_length=50, ref=dimensoes_ref),
                ft.TextField(label="Peso", max_length=50, ref=peso_ref),
                ft.TextField(
                    label="Quantidade", ref=quantidade_ref,
                    keyboard_type=ft.KeyboardType.NUMBER
                ),
                ft.Row(
                    [
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
                        )
                    ],
                ),
                ft.Row(
                    [
                        ft.ElevatedButton("Cadastrar", on_click=cadastrar_peca),
                        ft.ElevatedButton("Limpar", on_click=limpar_campos),
                        ft.ElevatedButton("Fechar", on_click=fechar_dialogo),
                    ], alignment=ft.MainAxisAlignment.SPACE_EVENLY),
            ]
        ),
        ref=cadastro_dialog_ref,
    )

    page.overlay.append(cadastro_dialog)

    # Função para abrir o diálogo
    def abrir_dialogo():
        cadastro_dialog_ref.current.open = True
        page.update()

    return abrir_dialogo
