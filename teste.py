import sqlite3
from datetime import datetime

# Define o caminho para o banco de dados
DATABASE = 'instance/sistema_seguranca.db'

def inserir_dados_teste():
    """
    Insere dados de teste nas tabelas colaboradores, epis e entregas_epi.
    """
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    db = conn.cursor()

    try:
        # Inserir colaboradores
        colaboradores_data = [
            ('João da Silva', '12.345.678-9', '123.456.789-01', 'Auxiliar de Produção', 'Produção', '2024-01-15', 'Ativo', None),
            ('Maria Oliveira', '23.456.789-0', '234.567.890-12', 'Técnico de Segurança', 'Segurança', '2023-05-20', 'Ativo', None),
            ('Carlos Pereira', '34.567.890-1', '345.678.901-23', 'Gerente de Projetos', 'Administrativo', '2022-10-10', 'Desligado', '2025-03-01'),
        ]
        db.executemany("""
            INSERT INTO colaboradores (nome_completo, rg, cpf, funcao, setor, data_admissao, status, data_desligamento)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, colaboradores_data)

        # Inserir EPIs
        epis_data = [
            ('Capacete de Segurança', 'CA 12345', 'Capacete para proteção da cabeça', 'Fabricante A', '2025-05-10', 'Sim', 365, 50, 10),
            ('Luvas de Borracha', 'CA 67890', 'Luvas para proteção das mãos', 'Fabricante B', '2024-12-31', 'Sim', 180, 100, 20),
            ('Óculos de Proteção', 'CA 24680', 'Óculos para proteção dos olhos', 'Fabricante C', None, 'Nao', None, 200, 50),
            ('Máscara Respiratória', 'CA 13579', 'Máscara para proteção respiratória', 'Fabricante A', '2025-01-15', 'Sim', 90, 80, 15),
        ]
        db.executemany("""
            INSERT INTO epis (nome, ca, descricao, fabricante, data_validade, controlar_periodicidade, periodicidade_troca, quantidade_estoque, estoque_minimo)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, epis_data)

        # Inserir entregas/entradas de EPIs
        entregas_epi_data = [
            (1, 1, '2025-04-01', 2, 'Saída', None, None, None, None),         # EPI 1, Colab 1, Saída
            (1, 2, '2025-04-05', 3, 'Saída', None, None, None, None),         # EPI 1, Colab 2, Saída
            (1, None, '2025-04-10', 10, 'Entrada', 'NF001', 15.00, 150.00, 'Fornecedor X'),  # EPI 1, Entrada
            (2, None, '2025-04-15', 5, 'Entrada', 'NF002', 5.00, 25.00, 'Fornecedor Y'),    # EPI 2, Entrada
            (2, 1, '2025-04-20', 1, 'Saída', None, None, None, None),         # EPI 2, Colab 1, Saída
        ]
        db.executemany("""
            INSERT INTO entregas_epi (epi_id, colaborador_id, data_entrega, quantidade_entregue, tipo_movimentacao, nota_fiscal, preco_unitario, preco_total, fornecedor)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, entregas_epi_data)

        conn.commit()
        print("Dados de teste inseridos com sucesso!")

    except sqlite3.Error as e:
        print(f"Erro ao inserir dados de teste: {e}")

    finally:
        conn.close()

if __name__ == '__main__':
    inserir_dados_teste()