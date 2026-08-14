CREATE TABLE IF NOT EXISTS salas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo TEXT UNIQUE NOT NULL,
    nome TEXT NOT NULL,
    token_mestre TEXT UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS jogadores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sala_id INTEGER NOT NULL,
    nome TEXT NOT NULL,
    token TEXT UNIQUE NOT NULL,
    pontos INTEGER DEFAULT 0,
    FOREIGN KEY (sala_id) REFERENCES salas(id)
);

CREATE TABLE IF NOT EXISTS fichas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    jogador_id INTEGER UNIQUE NOT NULL,
    nome_personagem TEXT,
    habilidade TEXT,
    inventario TEXT,
    FOREIGN KEY (jogador_id) REFERENCES jogadores(id)
);

CREATE TABLE IF NOT EXISTS rolagens (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sala_id INTEGER NOT NULL,
    jogador_id INTEGER,
    dado TEXT NOT NULL,
    resultado INTEGER NOT NULL,
    data DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (sala_id) REFERENCES salas(id),
    FOREIGN KEY (jogador_id) REFERENCES jogadores(id)
);