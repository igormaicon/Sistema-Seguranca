DROP TABLE IF EXISTS colaboradores;

CREATE TABLE colaboradores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome_completo TEXT NOT NULL,
    rg TEXT NOT NULL UNIQUE,
    cpf TEXT NOT NULL UNIQUE,
    funcao TEXT NOT NULL,
    setor TEXT NOT NULL,
    data_admissao TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'Ativo',
    data_desligamento TEXT
);

DROP TABLE IF EXISTS epis;

DROP TABLE IF EXISTS epis;

CREATE TABLE epis (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL UNIQUE,
    ca TEXT,
    descricao TEXT NOT NULL,
    fabricante TEXT,
    data_validade TEXT,
    controlar_periodicidade TEXT NOT NULL DEFAULT 'Nao',
    periodicidade_troca INTEGER,
    quantidade_estoque INTEGER NOT NULL DEFAULT 0,
    estoque_minimo INTEGER NOT NULL DEFAULT 0
);

DROP TABLE IF EXISTS entregas_epi;

CREATE TABLE entregas_epi (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    epi_id INTEGER NOT NULL,
    colaborador_id INTEGER NOT NULL,
    data_entrega TEXT NOT NULL,
    quantidade_entregue INTEGER NOT NULL,
    FOREIGN KEY (epi_id) REFERENCES epis(id),
    FOREIGN KEY (colaborador_id) REFERENCES colaboradores(id)
);