import sqlite3

DATABASE = "database.db"


def conectar():
    conexao = sqlite3.connect(DATABASE)
    conexao.row_factory = sqlite3.Row
    return conexao


def inicializar_banco():
    conexao = conectar()

    with open("schema.sql", "r", encoding="utf-8") as arquivo:
        conexao.executescript(arquivo.read())

    conexao.commit()
    conexao.close()