import sqlite3
import json
from datetime import datetime

banco_dados_unico = "manutencao.db"

# Função para registrar logs no banco de dados
def registrar_log(tabela, registro_id, detalhes, usuario_responsavel):
    with sqlite3.connect(banco_dados_unico) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO logs_alteracoes (tabela_afetada, registro_id, detalhes, usuario_responsavel)
            VALUES (?, ?, ?, ?)
            """,
            (tabela, registro_id, json.dumps(detalhes), usuario_responsavel)
        )
        conn.commit()

# Função para buscar dados antigos de uma peça
def buscar_dados_peca(nome_peca):
    with sqlite3.connect(banco_dados_unico) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT descricao, fabricante, dimensoes, peso, quantidade, classe FROM pecas WHERE nome_peca = ?",
            (nome_peca,)
        )
        dados = cursor.fetchone()
        if dados:
            return {
                "descricao": dados[0],
                "fabricante": dados[1],
                "dimensoes": dados[2],
                "peso": dados[3],
                "quantidade": dados[4],
                "classe": dados[5],
            }
        return None

# Função para atualizar uma peça e registrar log
def atualizar_peca(nome_peca, descricao, fabricante, dimensoes, peso, quantidade, classe, usuario_responsavel):
    with sqlite3.connect(banco_dados_unico) as conn:
        cursor = conn.cursor()

        # Buscar dados antigos
        dados_antigos = buscar_dados_peca(nome_peca)
        if not dados_antigos:
            print("Peça não encontrada!")
            return

        # Atualizar os dados no banco
        cursor.execute(
            """
            UPDATE pecas
            SET descricao = ?, fabricante = ?, dimensoes = ?, peso = ?, quantidade = ?, classe = ?
            WHERE nome_peca = ?
            """,
            (descricao, fabricante, dimensoes, peso, quantidade, classe, nome_peca),
        )
        conn.commit()

        # Comparar os dados antigos e novos para identificar alterações
        dados_novos = {
            "descricao": descricao,
            "fabricante": fabricante,
            "dimensoes": dimensoes,
            "peso": peso,
            "quantidade": quantidade,
            "classe": classe,
        }

        alteracoes = {chave: {"antes": dados_antigos[chave], "depois": dados_novos[chave]}
                        for chave in dados_antigos if dados_antigos[chave] != dados_novos[chave]}

        # Se houver alterações, registrar no log
        if alteracoes:
            registrar_log(
                tabela="pecas",
                registro_id=nome_peca,
                detalhes=alteracoes,
                usuario_responsavel=usuario_responsavel
            )
            print(f"Alterações registradas: {alteracoes}")
        else:
            print("Nenhuma alteração foi feita.")
