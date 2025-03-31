import logging
from datetime import datetime
import sqlite3

from flask import Flask, render_template, request, g, redirect, url_for, jsonify

from database import get_db, init_db

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)


def get_current_year():
    return datetime.now().year


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
    return render_template('listar_colaboradores.html', colaboradores=colaboradores)


@app.route('/editar_colaborador/<int:id>')
def editar_colaborador(id):
    db = get_db()
    colaborador = db.execute("SELECT * FROM colaboradores WHERE id = ?", (id,)).fetchone()
    if colaborador:
        return render_template('editar_colaborador.html', colaborador=colaborador)
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
    return render_template('listar_epis.html', epis=epis)


@app.route('/editar_epi/<int:id>')
def editar_epi(id):
    db = get_db()
    epi = db.execute("SELECT * FROM epis WHERE id = ?", (id,)).fetchone()
    colaboradores = db.execute("SELECT * FROM colaboradores").fetchall()
    if epi:
        return render_template('editar_epi.html', epi=epi, colaboradores=colaboradores)
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


@app.route('/entregar_epi/<int:id>')
def entregar_epi(id):
    db = get_db()
    epis = db.execute("SELECT * FROM epis WHERE id = ?", (id,)).fetchone()
    colaboradores = db.execute("SELECT * FROM colaboradores").fetchall()
    if epis:
        return render_template('entregar_epi.html', epis=epis, colaboradores=colaboradores)
    else:
        return "EPI não encontrado."


@app.route('/entrega_epi', methods=['POST'])
def entrega_epi():
    epi_id = request.form.get('epi_id')
    colaborador_id = request.form.getlist('colaborador_id')
    data_entrega = request.form['data_entrega']
    quantidade_entregue = request.form['quantidade_entregue']

    db = get_db()
    try:
        db.execute("""
            INSERT INTO entregas_epi (epi_id, colaborador_id, data_entrega, quantidade_entregue)
            VALUES (?, ?, ?, ?)
        """, (epi_id, ','.join(colaborador_id), data_entrega, quantidade_entregue))

        db.execute("""
            UPDATE epis SET quantidade_estoque = quantidade_estoque - ?
            WHERE id = ?
        """, (quantidade_entregue, epi_id))

        db.commit()
        app.logger.info(f"EPI com ID {epi_id} entregue ao colaborador com ID {colaborador_id}")
        return redirect(url_for('listar_epis'))
    except sqlite3.IntegrityError as e:
        return f"Erro ao registrar entrega: {e}. Já existe um EPI com este nome. <a href='/entregar_epi/{epi_id}'>Tentar novamente</a>"


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
    return render_template('listar_entregas_epi.html', entregas=entregas, epis=epis, colaboradores=colaboradores)


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

if __name__ == '__main__':
    app.run(debug=True)