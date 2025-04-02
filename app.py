import logging
from datetime import datetime
import sqlite3

from flask import Flask, render_template, request, g, redirect, url_for, jsonify

from database import get_db, init_db

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)


def get_current_year():
    return datetime.now().year

def formatar_data(data):
    if data:
        data_obj = datetime.strptime(data, '%Y-%m-%d').date()
        return data_obj.strftime('%d/%m/%Y')
    return None

app.jinja_env.globals['year'] = get_current_year


@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()


@app.cli.command('init-db')
def initdb_command():
    """Inicializa o banco de dados."""
    init_db()
    print('Banco de dados inicializado.')


@app.route('/')
def pagina_principal():
    return render_template('pagina_principal.html')


@app.route('/colaboradores')
def colaboradores():
    db = get_db()
    total_ativos = db.execute("SELECT COUNT(*) FROM colaboradores WHERE status = 'Ativo'").fetchone()[0]
    total_desligados = db.execute("SELECT COUNT(*) FROM colaboradores WHERE status = 'Desligado'").fetchone()[0]
    colaboradores_por_setor = {}
    rows = db.execute("SELECT setor, COUNT(*) FROM colaboradores GROUP BY setor").fetchall()
    for row in rows:
        colaboradores_por_setor[row['setor']] = row[1]

    return render_template('colaboradores.html',
                           total_ativos=total_ativos,
                           total_desligados=total_desligados,
                           colaboradores_por_setor=colaboradores_por_setor)


@app.route('/cadastrar_colaborador')
def cadastrar_colaborador():
    return render_template('cadastrar_colaborador.html')


@app.route('/cadastro_colaborador', methods=['POST'])
def cadastro_colaborador():
    if request.method == 'POST':
        nome_completo = request.form['nome_completo']
        rg = request.form['rg']
        cpf = request.form['cpf']
        funcao = request.form['funcao']
        setor = request.form['setor']
        data_admissao = request.form['data_admissao']
        status = request.form['status']
        data_desligamento = request.form.get('data_desligamento')

        if status == "Ativo":
            data_desligamento = None

        db = get_db()
        try:
            db.execute("""
                INSERT INTO colaboradores (nome_completo, rg, cpf, funcao, setor, data_admissao, status, data_desligamento)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (nome_completo, rg, cpf, funcao, setor, data_admissao, status, data_desligamento))
            db.commit()
            app.logger.info(f"Colaborador cadastrado: {nome_completo}")
            return "Colaborador cadastrado com sucesso! <a href='/colaboradores'>Voltar para Gerenciamento de Colaboradores</a>"
        except sqlite3.IntegrityError as e:
            return f"Erro ao cadastrar: {e}. Já existe um colaborador com este RG ou CPF. <a href='/cadastrar_colaborador'>Tentar novamente</a>"


@app.route('/listar_colaboradores')
def listar_colaboradores():
    db = get_db()
    status_filtro = request.args.get('status')
    query = "SELECT * FROM colaboradores"
    params = []

    if status_filtro:
        query += " WHERE status = ?"
        params.append(status_filtro)

    colaboradores = db.execute(query, params).fetchall()

    colaboradores_formatados = []
    for colaborador in colaboradores:
        colaborador_dict = dict(colaborador)
        colaborador_dict['data_admissao'] = formatar_data(colaborador_dict['data_admissao'])
        if colaborador_dict['data_desligamento']:
            colaborador_dict['data_desligamento'] = formatar_data(colaborador_dict['data_desligamento'])
        colaboradores_formatados.append(colaborador_dict)

    return render_template('listar_colaboradores.html', colaboradores=colaboradores_formatados)


@app.route('/editar_colaborador/<int:id>')
def editar_colaborador(id):
    db = get_db()
    colaborador = db.execute("SELECT * FROM colaboradores WHERE id = ?", (id,)).fetchone()
    if colaborador:
        colaborador_dict = dict(colaborador)
        colaborador_dict['data_admissao'] = formatar_data(colaborador_dict['data_admissao'])
        if colaborador_dict['data_desligamento']:
            colaborador_dict['data_desligamento'] = formatar_data(colaborador_dict['data_desligamento'])
        return render_template('editar_colaborador.html', colaborador=colaborador_dict)
    else:
        return "Colaborador não encontrado."


@app.route('/editar_colaborador/<int:id>', methods=['POST'])
def editar_colaborador_post(id):
    if request.method == 'POST':
        nome_completo = request.form['nome_completo']
        rg = request.form['rg']
        cpf = request.form['cpf']
        funcao = request.form['funcao']
        setor = request.form['setor']
        data_admissao = request.form['data_admissao']
        status = request.form['status']
        data_desligamento = request.form.get('data_desligamento')

        if status == "Ativo":
            data_desligamento = None

        db = get_db()
        try:
            db.execute("""
                UPDATE colaboradores SET nome_completo = ?, rg = ?, cpf = ?, funcao = ?, setor = ?, data_admissao = ?, status = ?, data_desligamento = ?
                WHERE id = ?
            """, (nome_completo, rg, cpf, funcao, setor, data_admissao, status, data_desligamento, id))
            db.commit()
            app.logger.info(f"Colaborador com ID {id} editado: {nome_completo}")
            return redirect(url_for('listar_colaboradores'))
        except sqlite3.IntegrityError as e:
            return f"Erro ao editar: {e}. Já existe um colaborador com este RG ou CPF. <a href='/editar_colaborador/{id}'>Tentar novamente</a>"


@app.route('/excluir_colaborador/<int:id>')
def excluir_colaborador(id):
    db = get_db()
    db.execute("DELETE FROM colaboradores WHERE id = ?", (id,))
    db.commit()
    app.logger.info(f"Colaborador com ID {id} excluído")
    return redirect(url_for('listar_colaboradores'))


@app.route('/epis')
def epis():
    return render_template('epis.html')


@app.route('/cadastrar_epi')
def cadastrar_epi():
    return render_template('cadastrar_epi.html')


@app.route('/cadastro_epi', methods=['POST'])
def cadastro_epi():
    if request.method == 'POST':
        nome = request.form['nome']
        ca = request.form['ca']
        descricao = request.form.get('descricao')
        fabricante = request.form.get('fabricante')
        data_validade = request.form.get('data_validade')
        controlar_periodicidade = request.form.get('controlar_periodicidade')
        periodicidade_troca = request.form.get('periodicidade_troca')
        quantidade_estoque = request.form['quantidade_estoque']
        estoque_minimo = request.form['estoque_minimo']

        if controlar_periodicidade == "Nao":
            periodicidade_troca = None

        db = get_db()
        try:
            db.execute("""
                INSERT INTO epis (nome, ca, descricao, fabricante, data_validade, controlar_periodicidade, periodicidade_troca, quantidade_estoque, estoque_minimo)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (nome, ca, descricao, fabricante, data_validade, controlar_periodicidade, periodicidade_troca, quantidade_estoque, estoque_minimo))
            db.commit()
            app.logger.info(f"EPI cadastrado: {nome}")
            return "EPI cadastrado com sucesso! <a href='/epis'>Voltar para Gerenciamento de EPIs</a>"
        except sqlite3.IntegrityError as e:
            return f"Erro ao cadastrar: Já existe um EPI com este nome. <a href='/cadastrar_epi'>Tentar novamente</a>"


@app.route('/listar_epis')
def listar_epis():
    db = get_db()
    epis = db.execute("SELECT * FROM epis").fetchall()
    hoje = datetime.now().date()  # Obtém a data atual

    epis_com_status = []  # Lista para armazenar os EPIs com o status de validade

    for epi in epis:
        epi_dict = dict(epi)  # Converte o sqlite3.Row para um dicionário
        if epi_dict['data_validade']:
            data_validade = datetime.strptime(epi_dict['data_validade'], '%Y-%m-%d').date()
            dias_para_vencer = (data_validade - hoje).days

            if dias_para_vencer <= 0:
                epi_dict['status_validade'] = 'Vencido'
            elif dias_para_vencer <= 30:
                epi_dict['status_validade'] = 'Próximo do Vencimento'
            else:
                epi_dict['status_validade'] = 'OK'
            epi_dict['data_validade'] = formatar_data(epi_dict['data_validade'])
        else:
            epi_dict['status_validade'] = 'Sem Data'  # Ou outro valor padrão, se preferir

        epis_com_status.append(epi_dict)  # Adiciona o dicionário à lista

    return render_template('listar_epis.html', epis=epis_com_status)


@app.route('/editar_epi/<int:id>')
def editar_epi(id):
    db = get_db()
    epi = db.execute("SELECT * FROM epis WHERE id = ?", (id,)).fetchone()
    colaboradores = db.execute("SELECT * FROM colaboradores").fetchall()
    if epi:
        epi_dict = dict(epi)
        epi_dict['data_validade'] = formatar_data(epi_dict['data_validade'])
        return render_template('editar_epi.html', epi=epi_dict, colaboradores=colaboradores)
    else:
        return "EPI não encontrado."


@app.route('/editar_epi/<int:id>', methods=['POST'])
def editar_epi_post(id):
    nome = request.form['nome']
    ca = request.form['ca']
    descricao = request.form.get('descricao')
    fabricante = request.form.get('fabricante')
    data_validade = request.form.get('data_validade')
    controlar_periodicidade = request.form.get('controlar_periodicidade')
    periodicidade_troca = request.form.get('periodicidade_troca')
    quantidade_estoque = request.form['quantidade_estoque']
    estoque_minimo = request.form['estoque_minimo']

    if controlar_periodicidade == "Nao":
        periodicidade_troca = None

    db = get_db()
    try:
        db.execute("""
            UPDATE epis SET nome = ?, ca = ?, descricao = ?, fabricante = ?, data_validade = ?, controlar_periodicidade = ?, periodicidade_troca = ?, quantidade_estoque = ?, estoque_minimo = ?
            WHERE id = ?
        """, (nome, ca, descricao, fabricante, data_validade, controlar_periodicidade, periodicidade_troca, quantidade_estoque, estoque_minimo, id))
        db.commit()
        app.logger.info(f"EPI com ID {id} editado: {nome}")
        return redirect(url_for('listar_epis'))
    except sqlite3.IntegrityError as e:
        return f"Erro ao editar: {e}. Já existe um EPI com este nome. <a href='/editar_epi/{id}'>Tentar novamente</a>"


@app.route('/excluir_epi/<int:id>')
def excluir_epi(id):
    db = get_db()
    db.execute("DELETE FROM epis WHERE id = ?", (id,))
    db.commit()
    app.logger.info(f"EPI com ID {id} excluído")
    return redirect(url_for('listar_epis'))


@app.route('/entregar_epi')  # Remova o parâmetro <int:id>
def entregar_epi():
    db = get_db()
    epis = db.execute("SELECT * FROM epis").fetchall()  # Busca todos os EPIs
    colaboradores = db.execute("SELECT * FROM colaboradores").fetchall()
    return render_template('entregar_epi.html', epis=epis, colaboradores=colaboradores)


@app.route('/entrega_epi', methods=['POST'])
def entrega_epi():
    epi_id = request.form.get('epi_id')
    colaborador_id = request.form.getlist('colaborador_id')
    data_entrega = request.form['data_entrega']
    quantidade_entregue = request.form['quantidade_entregue']

    db = get_db()
    try:
        for colab_id in colaborador_id:
            db.execute("""
                INSERT INTO entregas_epi (epi_id, colaborador_id, data_entrega, quantidade_entregue, tipo_movimentacao)
                VALUES (?, ?, ?, ?, ?)
            """, (epi_id, colab_id, data_entrega, quantidade_entregue, 'Saída'))  # Tipo 'Saída'

        db.execute("""
            UPDATE epis SET quantidade_estoque = quantidade_estoque - ?
            WHERE id = ?
        """, (quantidade_entregue, epi_id))

        db.commit()
        app.logger.info(f"EPI com ID {epi_id} entregue aos colaboradores com IDs {colaborador_id}")
        return redirect(url_for('epis'))
    except sqlite3.IntegrityError as e:
        return f"Erro ao registrar entrega: {e}. Já existe um EPI com este nome. <a href='/entregar_epi'>Tentar novamente</a>"

@app.route('/listar_entregas_epi')
def listar_entregas_epi():
    db = get_db()
    epi_id = request.args.getlist('epi_id')
    colaborador_id = request.args.getlist('colaborador_id')
    data_inicio = request.args.get('data_inicio')
    data_fim = request.args.get('data_fim')

    query = """
        SELECT e.nome as epi_nome, c.nome_completo as colaborador_nome, en.data_entrega, en.quantidade_entregue
        FROM entregas_epi en
        JOIN epis e ON en.epi_id = e.id
        JOIN colaboradores c ON en.colaborador_id = c.id
        WHERE 1
    """
    params = []

    if epi_id:
        query += " AND en.epi_id IN ({})".format(','.join(['?'] * len(epi_id)))
        params.extend(epi_id)

    if colaborador_id:
        query += " AND en.colaborador_id IN ({})".format(','.join(['?'] * len(colaborador_id)))
        params.extend(colaborador_id)

    if data_inicio:
        query += " AND en.data_entrega >= ?"
        params.append(data_inicio)

    if data_fim:
        query += " AND en.data_entrega <= ?"
        params.append(data_fim)

    entregas = db.execute(query, params).fetchall()
    epis = db.execute("SELECT * FROM epis").fetchall()
    colaboradores = db.execute("SELECT * FROM colaboradores").fetchall()

    entregas_formatadas = []
    for entrega in entregas:
        entrega_dict = dict(entrega)
        entrega_dict['data_entrega'] = formatar_data(entrega_dict['data_entrega'])
        entregas_formatadas.append(entrega_dict)

    return render_template('listar_entregas_epi.html', entregas=entregas_formatadas, epis=epis, colaboradores=colaboradores)

@app.route('/incidentes')
def incidentes():
    return render_template('incidentes.html')


@app.route('/acidentes')
def acidentes():
    return render_template('acidentes.html')


@app.route('/treinamentos')
def treinamentos():
    return render_template('treinamentos.html')

@app.route('/editar_entrega_epi/<int:id>', methods=['GET'])
def editar_entrega_epi(id):
    db = get_db()
    entrega = db.execute("""
        SELECT en.id, en.epi_id, en.colaborador_id, en.data_entrega, en.quantidade_entregue
        FROM entregas_epi en
        WHERE en.id = ?
    """, (id,)).fetchone()
    epis = db.execute("SELECT * FROM epis").fetchall()
    colaboradores = db.execute("SELECT * FROM colaboradores").fetchall()
    if entrega:
        return render_template('editar_entrega_epi.html', entrega=entrega, epis=epis, colaboradores=colaboradores)
    else:
        return "Entrega de EPI não encontrada."

@app.route('/editar_entrega_epi/<int:id>', methods=['POST'])
def editar_entrega_epi_post(id):
    epi_id = request.form['epi_id']
    colaborador_id = request.form['colaborador_id']
    data_entrega = request.form['data_entrega']
    quantidade_entregue = request.form['quantidade_entregue']

    db = get_db()
    db.execute("""
        UPDATE entregas_epi SET epi_id = ?, colaborador_id = ?, data_entrega = ?, quantidade_entregue = ?
        WHERE id = ?
    """, (epi_id, colaborador_id, data_entrega, quantidade_entregue, id))
    db.commit()
    app.logger.info(f"Entrega de EPI com ID {id} editada")
    return redirect(url_for('listar_entregas_epi'))

@app.route('/historico_entregas_colaborador/<int:colaborador_id>')
def historico_entregas_colaborador(colaborador_id):
    db = get_db()
    entregas = db.execute("""
        SELECT e.nome as epi_nome, en.data_entrega, en.quantidade_entregue
        FROM entregas_epi en
        JOIN epis e ON en.epi_id = e.id
        WHERE en.colaborador_id = ?
    """, (colaborador_id,)).fetchall()
    colaborador = db.execute("SELECT * FROM colaboradores WHERE id = ?", (colaborador_id,)).fetchone()
    return render_template('historico_entregas_colaborador.html', entregas=entregas, colaborador=colaborador)

@app.route('/entrada_epi')
def entrada_epi():
    db = get_db()
    epis = db.execute("SELECT * FROM epis").fetchall()
    return render_template('entrada_epi.html', epis=epis)

@app.route('/registrar_entrada_epi', methods=['POST'])
def registrar_entrada_epi():
    if request.method == 'POST':
        epi_id = request.form['epi_id']
        data_entrada = request.form['data_entrada']
        nota_fiscal = request.form['nota_fiscal']
        fornecedor = request.form['fornecedor']  # Novo campo
        quantidade = request.form['quantidade']
        preco_unitario = request.form['preco_unitario']
        preco_total = request.form['preco_total']

        db = get_db()
        try:
            db.execute("""
                INSERT INTO entregas_epi (epi_id, colaborador_id, data_entrega, quantidade_entregue, tipo_movimentacao, nota_fiscal, preco_unitario, preco_total, fornecedor)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (epi_id, None, data_entrada, quantidade, 'Entrada', nota_fiscal, preco_unitario, preco_total, fornecedor))  # Inclui fornecedor, colaborador_id é None

            # Atualizar a quantidade em estoque do EPI
            db.execute("""
                UPDATE epis SET quantidade_estoque = quantidade_estoque + ?
                WHERE id = ?
            """, (quantidade, epi_id))

            db.commit()
            app.logger.info(f"Entrada de EPI com ID {epi_id} registrada")
            return redirect(url_for('listar_epis'))
        except sqlite3.Error as e:
            return f"Erro ao registrar entrada: {e}. <a href='/entrada_epi'>Tentar novamente</a>"
    
@app.route('/historico_epi/<int:epi_id>')
def historico_epi(epi_id):
    db = get_db()
    epi = db.execute("SELECT * FROM epis WHERE id = ?", (epi_id,)).fetchone()

    # Filtros
    colaborador_id = request.args.get('colaborador_id')
    tipo_movimentacao = request.args.get('tipo_movimentacao')
    data_inicio = request.args.get('data_inicio')
    data_fim = request.args.get('data_fim')

    query = """
        SELECT c.nome_completo, en.data_entrega, en.quantidade_entregue, en.tipo_movimentacao,
               en.nota_fiscal, en.preco_unitario, en.preco_total, en.fornecedor, c.setor
        FROM entregas_epi en
        LEFT JOIN colaboradores c ON en.colaborador_id = c.id
        WHERE en.epi_id = ?
    """
    params = [epi_id]

    if colaborador_id:
        query += " AND en.colaborador_id = ?"
        params.append(colaborador_id)

    if tipo_movimentacao:
        query += " AND en.tipo_movimentacao = ?"
        params.append(tipo_movimentacao)

    if data_inicio:
        query += " AND en.data_entrega >= ?"
        params.append(data_inicio)

    if data_fim:
        query += " AND en.data_entrega <= ?"
        params.append(data_fim)

    historico = db.execute(query, params).fetchall()
    colaboradores = db.execute("SELECT * FROM colaboradores").fetchall()  # Para o filtro de colaborador

    historico_formatado = []
    existem_entradas = False
    existem_saidas = False

    for item in historico:
        item_dict = dict(item)
        item_dict['data_entrega'] = formatar_data(item_dict['data_entrega'])
        if item_dict['tipo_movimentacao'] == 'Entrada':
            existem_entradas = True
        elif item_dict['tipo_movimentacao'] == 'Saída':
            existem_saidas = True
        historico_formatado.append(item_dict)

    return render_template('historico_epi.html', epi=epi, historico=historico_formatado, colaboradores=colaboradores, existem_entradas=existem_entradas, existem_saidas=existem_saidas)

@app.route('/listar_entradas_epi')
def listar_entradas_epi():
    db = get_db()
    entradas = db.execute("""
        SELECT e.nome as epi_nome, en.data_entrega, en.quantidade_entregue, en.nota_fiscal,
               en.preco_unitario, en.preco_total, en.fornecedor
        FROM entregas_epi en
        JOIN epis e ON en.epi_id = e.id
        WHERE en.tipo_movimentacao = 'Entrada'
    """).fetchall()
    return render_template('listar_entradas_epi.html', entradas=entradas)

@app.route('/registrar_incidente', methods=['POST'])
def registrar_incidente():
    if request.method == 'POST':
        data_incidente = request.form['data_incidente']
        hora_incidente = request.form['hora_incidente']
        local_incidente = request.form['local_incidente']
        descricao_incidente = request.form['descricao_incidente']
        tipo_incidente = request.form['tipo_incidente']
        gravidade_incidente = request.form['gravidade_incidente']
        colaboradores_envolvidos = request.form['colaboradores_envolvidos']
        equipamentos_envolvidos = request.form['equipamentos_envolvidos']
        acoes_tomadas = request.form.get('acoes_tomadas')  # Use .get() para campos não obrigatórios

        db = get_db()
        try:
            db.execute("""
                INSERT INTO incidentes (data_incidente, hora_incidente, local_incidente, descricao_incidente,
                                        tipo_incidente, gravidade_incidente, colaboradores_envolvidos,
                                        equipamentos_envolvidos, acoes_tomadas)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (data_incidente, hora_incidente, local_incidente, descricao_incidente,
                  tipo_incidente, gravidade_incidente, colaboradores_envolvidos,
                  equipamentos_envolvidos, acoes_tomadas))
            db.commit()
            app.logger.info(f"Incidente registrado: {descricao_incidente}")
            return "Incidente registrado com sucesso! <a href='/incidentes'>Voltar para Incidentes</a>"
        except sqlite3.Error as e:
            return f"Erro ao registrar incidente: {e}. <a href='/incidentes'>Tentar novamente</a>"

@app.route('/listar_incidentes')
def listar_incidentes():
    db = get_db()
    query = "SELECT * FROM incidentes WHERE 1"  # Inicializa a query com uma condição verdadeira
    params = []

    # Filtrar por data
    data_incidente = request.args.get('data_incidente')
    if data_incidente:
        query += " AND data_incidente = ?"
        params.append(data_incidente)

    # Filtrar por tipo
    tipo_incidente = request.args.get('tipo_incidente')
    if tipo_incidente:
        query += " AND tipo_incidente = ?"
        params.append(tipo_incidente)

    # Filtrar por gravidade
    gravidade_incidente = request.args.get('gravidade_incidente')
    if gravidade_incidente:
        query += " AND gravidade_incidente = ?"
        params.append(gravidade_incidente)

    # Pesquisar por descrição
    pesquisa = request.args.get('pesquisa')
    if pesquisa:
        query += " AND descricao_incidente LIKE ?"
        params.append(f"%{pesquisa}%")  # Adiciona os curingas % para pesquisa "contém"

    incidentes = db.execute(query, params).fetchall()
    return render_template('listar_incidentes.html', incidentes=incidentes)

@app.route('/cadastro_incidente', methods=['POST'])
def cadastro_incidente():
    if request.method == 'POST':
        data_incidente = request.form['data_incidente']
        hora_incidente = request.form['hora_incidente']
        local_incidente = request.form['local_incidente']
        descricao_incidente = request.form['descricao_incidente']
        tipo_incidente = request.form['tipo_incidente']
        gravidade_incidente = request.form['gravidade_incidente']
        colaboradores_envolvidos = request.form['colaboradores_envolvidos']
        equipamentos_envolvidos = request.form['equipamentos_envolvidos']
        acoes_tomadas = request.form.get('acoes_tomadas')  # Use .get() para campos não obrigatórios

        db = get_db()
        try:
            db.execute("""
                INSERT INTO incidentes (data_incidente, hora_incidente, local_incidente, descricao_incidente,
                                        tipo_incidente, gravidade_incidente, colaboradores_envolvidos,
                                        equipamentos_envolvidos, acoes_tomadas)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (data_incidente, hora_incidente, local_incidente, descricao_incidente,
                  tipo_incidente, gravidade_incidente, colaboradores_envolvidos,
                  equipamentos_envolvidos, acoes_tomadas))
            db.commit()
            app.logger.info(f"Incidente registrado: {descricao_incidente}")
            return "Incidente registrado com sucesso! <a href='/incidentes'>Voltar para Incidentes</a>"
        except sqlite3.Error as e:
            return f"Erro ao registrar incidente: {e}. <a href='/incidentes'>Tentar novamente</a>"
        
@app.route('/cadastrar_incidente')
def cadastrar_incidente():
    return render_template('cadastrar_incidente.html')

@app.route('/detalhes_incidente/<int:id>')
def detalhes_incidente(id):
    db = get_db()
    incidente = db.execute("SELECT * FROM incidentes WHERE id = ?", (id,)).fetchone()
    return render_template('detalhes_incidente.html', incidente=incidente)

@app.route('/excluir_incidente/<int:id>')
def excluir_incidente(id):
    db = get_db()
    db.execute("DELETE FROM incidentes WHERE id = ?", (id,))
    db.commit()
    app.logger.info(f"Incidente com ID {id} excluído")
    return redirect(url_for('listar_incidentes'))

@app.route('/editar_incidente/<int:id>', methods=['GET'])
def editar_incidente(id):
    db = get_db()
    incidente = db.execute("SELECT * FROM incidentes WHERE id = ?", (id,)).fetchone()
    if incidente:
        return render_template('editar_incidente.html', incidente=incidente)
    else:
        return "Incidente não encontrado."
    
@app.route('/editar_incidente/<int:id>', methods=['POST'])
def editar_incidente_post(id):
    if request.method == 'POST':
        data_incidente = request.form['data_incidente']
        hora_incidente = request.form['hora_incidente']
        local_incidente = request.form['local_incidente']
        descricao_incidente = request.form['descricao_incidente']
        tipo_incidente = request.form['tipo_incidente']
        gravidade_incidente = request.form['gravidade_incidente']
        colaboradores_envolvidos = request.form['colaboradores_envolvidos']
        equipamentos_envolvidos = request.form['equipamentos_envolvidos']
        acoes_tomadas = request.form.get('acoes_tomadas')

        db = get_db()
        try:
            db.execute("""
                UPDATE incidentes SET data_incidente = ?, hora_incidente = ?, local_incidente = ?,
                                    descricao_incidente = ?, tipo_incidente = ?, gravidade_incidente = ?,
                                    colaboradores_envolvidos = ?, equipamentos_envolvidos = ?, acoes_tomadas = ?
                WHERE id = ?
            """, (data_incidente, hora_incidente, local_incidente, descricao_incidente,
                  tipo_incidente, gravidade_incidente, colaboradores_envolvidos,
                  equipamentos_envolvidos, acoes_tomadas, id))
            db.commit()
            app.logger.info(f"Incidente com ID {id} editado")
            return redirect(url_for('listar_incidentes'))
        except sqlite3.Error as e:
            return f"Erro ao editar incidente: {e}. <a href='/editar_incidente/{id}'>Tentar novamente</a>"
        
@app.route('/registrar_acidente', methods=['POST'])
def registrar_acidente():
    if request.method == 'POST':
        data_acidente = request.form['data_acidente']
        hora_acidente = request.form['hora_acidente']
        local_acidente = request.form['local_acidente']
        descricao_acidente = request.form['descricao_acidente']
        tipo_acidente = request.form['tipo_acidente']
        gravidade_acidente = request.form['gravidade_acidente']
        colaboradores_envolvidos = request.form['colaboradores_envolvidos']
        equipamentos_envolvidos = request.form['equipamentos_envolvidos']
        acoes_tomadas = request.form.get('acoes_tomadas')
        consequencias_acidente = request.form.get('consequencias_acidente')
        afastamento_necessario = request.form.get('afastamento_necessario')

        db = get_db()
        try:
            db.execute("""
                INSERT INTO acidentes (data_acidente, hora_acidente, local_acidente, descricao_acidente,
                                        tipo_acidente, gravidade_acidente, colaboradores_envolvidos,
                                        equipamentos_envolvidos, acoes_tomadas, consequencias_acidente,
                                        afastamento_necessario)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (data_acidente, hora_acidente, local_acidente, descricao_acidente,
                  tipo_acidente, gravidade_acidente, colaboradores_envolvidos,
                  equipamentos_envolvidos, acoes_tomadas, consequencias_acidente,
                  afastamento_necessario))
            db.commit()
            app.logger.info(f"Acidente registrado: {descricao_acidente}")
            return "Acidente registrado com sucesso! <a href='/acidentes'>Voltar para Acidentes</a>"
        except sqlite3.Error as e:
            return f"Erro ao registrar acidente: {e}. <a href='/acidentes'>Tentar novamente</a>"

@app.route('/listar_acidentes')
def listar_acidentes():
    db = get_db()
    acidentes = db.execute("SELECT * FROM acidentes").fetchall()
    return render_template('listar_acidentes.html', acidentes=acidentes)

@app.route('/cadastro_acidente', methods=['POST'])
def cadastro_acidente():
    if request.method == 'POST':
        data_acidente = request.form['data_acidente']
        hora_acidente = request.form['hora_acidente']
        local_acidente = request.form['local_acidente']
        descricao_acidente = request.form['descricao_acidente']
        tipo_acidente = request.form['tipo_acidente']
        gravidade_acidente = request.form['gravidade_acidente']
        colaboradores_envolvidos = request.form['colaboradores_envolvidos']
        equipamentos_envolvidos = request.form['equipamentos_envolvidos']
        acoes_tomadas = request.form.get('acoes_tomadas')
        consequencias_acidente = request.form.get('consequencias_acidente')
        afastamento_necessario = request.form.get('afastamento_necessario')

        db = get_db()
        try:
            db.execute("""
                INSERT INTO acidentes (data_acidente, hora_acidente, local_acidente, descricao_acidente,
                                        tipo_acidente, gravidade_acidente, colaboradores_envolvidos,
                                        equipamentos_envolvidos, acoes_tomadas, consequencias_acidente,
                                        afastamento_necessario)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (data_acidente, hora_acidente, local_acidente, descricao_acidente,
                  tipo_acidente, gravidade_acidente, colaboradores_envolvidos,
                  equipamentos_envolvidos, acoes_tomadas, consequencias_acidente,
                  afastamento_necessario))
            db.commit()
            app.logger.info(f"Acidente registrado: {descricao_acidente}")
            return "Acidente registrado com sucesso! <a href='/acidentes'>Voltar para Acidentes</a>"
        except sqlite3.Error as e:
            return f"Erro ao registrar acidente: {e}. <a href='/cadastrar_acidente'>Tentar novamente</a>"
        
@app.route('/cadastrar_acidente')
def cadastrar_acidente():
    return render_template('cadastrar_acidente.html')

@app.route('/registrar_treinamento', methods=['POST'])
def registrar_treinamento():
    if request.method == 'POST':
        titulo_treinamento = request.form['titulo_treinamento']
        descricao_treinamento = request.form['descricao_treinamento']
        data_treinamento = request.form['data_treinamento']
        hora_treinamento = request.form['hora_treinamento']
        local_treinamento = request.form['local_treinamento']
        instrutor_treinamento = request.form['instrutor_treinamento']
        colaboradores_participantes = request.form.get('colaboradores_participantes')
        carga_horaria_treinamento = request.form['carga_horaria_treinamento']
        conteudo_programatico_treinamento = request.form.get('conteudo_programatico_treinamento')
        material_disponibilizado_treinamento = request.form.get('material_disponibilizado_treinamento')
        observacoes_treinamento = request.form.get('observacoes_treinamento')

        db = get_db()
        try:
            db.execute("""
                INSERT INTO treinamentos (titulo_treinamento, descricao_treinamento, data_treinamento,
                                          hora_treinamento, local_treinamento, instrutor_treinamento,
                                          colaboradores_participantes, carga_horaria_treinamento,
                                          conteudo_programatico_treinamento, material_disponibilizado_treinamento,
                                          observacoes_treinamento)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (titulo_treinamento, descricao_treinamento, data_treinamento, hora_treinamento,
                  local_treinamento, instrutor_treinamento, colaboradores_participantes,
                  carga_horaria_treinamento, conteudo_programatico_treinamento,
                  material_disponibilizado_treinamento, observacoes_treinamento))
            db.commit()
            app.logger.info(f"Treinamento registrado: {titulo_treinamento}")
            return "Treinamento registrado com sucesso! <a href='/treinamentos'>Voltar para Treinamentos</a>"
        except sqlite3.Error as e:
            return f"Erro ao registrar treinamento: {e}. <a href='/treinamentos'>Tentar novamente</a>"
        
@app.route('/listar_treinamentos')
def listar_treinamentos():
    db = get_db()
    treinamentos = db.execute("SELECT * FROM treinamentos").fetchall()
    return render_template('listar_treinamentos.html', treinamentos=treinamentos)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')