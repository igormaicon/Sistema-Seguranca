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
    colaborador_id INTEGER,
    data_entrega TEXT NOT NULL,
    quantidade_entregue INTEGER NOT NULL,
    tipo_movimentacao TEXT NOT NULL,
    nota_fiscal TEXT,
    preco_unitario REAL,
    preco_total REAL,
    fornecedor TEXT,        -- Nova coluna
    FOREIGN KEY (epi_id) REFERENCES epis(id),
    FOREIGN KEY (colaborador_id) REFERENCES colaboradores(id)
);

DROP TABLE IF EXISTS entradas_epi;

CREATE TABLE entradas_epi (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    epi_id INTEGER NOT NULL,
    data_entrada TEXT NOT NULL,
    nota_fiscal TEXT,
    quantidade INTEGER NOT NULL,
    preco_unitario REAL NOT NULL,
    preco_total REAL NOT NULL,
    FOREIGN KEY (epi_id) REFERENCES epis(id)
);

DROP TABLE IF EXISTS incidentes;

CREATE TABLE incidentes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    data_incidente TEXT NOT NULL,
    hora_incidente TEXT NOT NULL,
    local_incidente TEXT NOT NULL,
    descricao_incidente TEXT NOT NULL,
    tipo_incidente TEXT NOT NULL,
    gravidade_incidente TEXT NOT NULL,
    colaboradores_envolvidos TEXT,
    equipamentos_envolvidos TEXT,
    acoes_tomadas TEXT
);

DROP TABLE IF EXISTS acidentes;

CREATE TABLE acidentes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    data_acidente TEXT NOT NULL,
    hora_acidente TEXT NOT NULL,
    local_acidente TEXT NOT NULL,
    descricao_acidente TEXT NOT NULL,
    tipo_acidente TEXT NOT NULL,
    gravidade_acidente TEXT NOT NULL,
    colaboradores_envolvidos TEXT,
    equipamentos_envolvidos TEXT,
    acoes_tomadas TEXT,
    consequencias_acidente TEXT,
    afastamento_necessario TEXT
);

DROP TABLE IF EXISTS treinamentos;

CREATE TABLE treinamentos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    titulo_treinamento TEXT NOT NULL,
    descricao_treinamento TEXT NOT NULL,
    tipo_treinamento TEXT NOT NULL,  -- Novo campo
    data_treinamento TEXT NOT NULL,
    hora_treinamento TEXT NOT NULL,
    local_treinamento TEXT NOT NULL,
    instrutor_treinamento TEXT NOT NULL,
    colaboradores_participantes TEXT,
    carga_horaria_treinamento INTEGER NOT NULL,
    unidade_carga_horaria TEXT NOT NULL, -- Novo campo
    conteudo_programatico_treinamento TEXT,
    material_disponibilizado_treinamento TEXT,
    observacoes_treinamento TEXT,
    status TEXT NOT NULL       -- Novo campo
);