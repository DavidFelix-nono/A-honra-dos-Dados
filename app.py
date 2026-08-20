from flask import Flask, render_template, request, redirect, session, jsonify
from flask_socketio import SocketIO, join_room
from database import inicializar_banco, conectar
import secrets
import string
import random

app = Flask(__name__)
app.secret_key = "chave-do-projeto"
# Cria o SocketIO ligado ao nosso servidor Flask.
socketio = SocketIO(app)

inicializar_banco()


@app.route("/")
def inicio():
    return render_template("index.html")


@app.route("/criar-sala", methods=["GET", "POST"])
def criar_sala():

    if request.method == "POST":
        nome = request.form["nome"]
        nome_mestre = request.form["nome_mestre"]
        senha_mestre = request.form["senha_mestre"]

        caracteres = string.ascii_uppercase + string.digits
        codigo = "".join(secrets.choice(caracteres) for _ in range(5))

        token_mestre = secrets.token_hex(32)

        conexao = conectar()

        sala_id = conexao.execute(
            """
            INSERT INTO salas (codigo, nome, token_mestre, nome_mestre, senha_mestre)
            VALUES (?, ?, ?, ?, ?)
            """,
            (codigo, nome, token_mestre, nome_mestre, senha_mestre)
        ).lastrowid

        conexao.commit()
        conexao.close()

        session["token_mestre"] = token_mestre
        session["sala_id"] = sala_id
        # Usamos session para!
        # Quem sou eu?
        #Qual é meu ID?
        #Qual sala estou?
        #Sou o Mestre?
        # session é um dicionario que guarda informações do usuário entre requisições / rotas, como se fosse um cookie seguro.

        return redirect("/mestre")

    return render_template("criar_sala.html")

@app.route("/entrar-sala", methods=["GET", "POST"])
def entrar_sala():

    if request.method == "POST":

        codigo = request.form["codigo"]
        nome = request.form["nome"]
        senha = request.form["senha"]

        conexao = conectar()

        # 1. Procuramos a sala pelo código
        sala = conexao.execute(
            "SELECT * FROM salas WHERE codigo = ?",
            (codigo,)
        ).fetchone()

        if sala is None:
            conexao.close()
            return "Sala não encontrada."

        # =========================================================
        # 2. PRIMEIRO verificamos se é o MESTRE
        # =========================================================

        if (
            nome == sala["nome_mestre"]
            and senha == sala["senha_mestre"]
        ):

            conexao.close()

            # Criamos a sessão do mestre
            session.clear()

            session["token_mestre"] = sala["token_mestre"]
            session["sala_id"] = sala["id"]

            return redirect("/mestre")

        # =========================================================
        # 3. Se não for mestre, procuramos um jogador
        # =========================================================

        jogador = conexao.execute(
            """
            SELECT * FROM jogadores
            WHERE sala_id = ? AND nome = ?
            """,
            (sala["id"], nome)
        ).fetchone()

        # =========================================================
        # 4. Jogador existente
        # =========================================================

        if jogador is not None:

            if jogador["senha"] != senha:
                conexao.close()
                return "Senha incorreta."

            conexao.close()

            session.clear()

            session["jogador_id"] = jogador["id"]
            session["sala_id"] = sala["id"]

            return redirect("/jogador")

        # =========================================================
        # 5. Jogador novo
        # =========================================================

        token_jogador = secrets.token_hex(32)

        jogador_id = conexao.execute(
            """
            INSERT INTO jogadores (sala_id, nome, senha, token)
            VALUES (?, ?, ?, ?)
            """,
            (sala["id"], nome, senha, token_jogador)
        ).lastrowid

        conexao.commit()
        conexao.close()

        session.clear()

        session["jogador_id"] = jogador_id
        session["sala_id"] = sala["id"]

        return redirect("/jogador")

    return render_template("entrar_sala.html")


@app.route("/mestre")
def mestre():

    token_mestre = session.get("token_mestre")
    sala_id = session.get("sala_id")

    if token_mestre is None or sala_id is None:
        return "Você não é mestre de nenhuma sala."

    conexao = conectar()

    sala = conexao.execute(
        """
        SELECT * FROM salas
        WHERE id = ? AND token_mestre = ?
        """,
        (sala_id, token_mestre)
    ).fetchone()

    if sala is None:
        conexao.close()
        return "Você não é o mestre desta sala."

    # Busca todas as rolagens dessa sala,
    # começando da mais recente.
    rolagens = conexao.execute(
        """
        SELECT
            rolagens.*,
            jogadores.nome AS nome_jogador
        FROM rolagens
        LEFT JOIN jogadores
            ON rolagens.jogador_id = jogadores.id
        WHERE rolagens.sala_id = ?
        ORDER BY rolagens.id DESC
        """,
        (sala_id,)
    ).fetchall()

    conexao.close()

    return render_template(
        "mestre.html",
        sala=sala,
        rolagens=rolagens
    )

 
@app.route("/jogador")
def jogador():

    jogador_id = session.get("jogador_id")

    if jogador_id is None:
        return "Você não está em nenhuma sala."

    conexao = conectar()

    jogador = conexao.execute(
        """
        SELECT * FROM jogadores
        WHERE id = ?
        """,
        (jogador_id,)
    ).fetchone()

    if jogador is None:
        conexao.close()
        return "Jogador não encontrado."

    ficha = conexao.execute(
        "SELECT * FROM fichas WHERE jogador_id = ?",
        (jogador_id,)
    ).fetchone()

    # Busca todas as rolagens da sala do jogador.
    rolagens = conexao.execute(
        """
        SELECT
            rolagens.*,
            jogadores.nome AS nome_jogador
        FROM rolagens
        LEFT JOIN jogadores
            ON rolagens.jogador_id = jogadores.id
        WHERE rolagens.sala_id = ?
        ORDER BY rolagens.id DESC
        """,
        (jogador["sala_id"],)
    ).fetchall()

    conexao.close()

    return render_template(
        "jogador.html",
        jogador=jogador,
        ficha=ficha,
        rolagens=rolagens
    )

@app.route("/criar-ficha", methods=["GET", "POST"])
def criar_ficha():

    jogador_id = session.get("jogador_id")

    if jogador_id is None:
        return "Você não está em nenhuma sala."

    if request.method == "POST":

        nome_personagem = request.form["nome_personagem"]

        conexao = conectar()

        conexao.execute(
            """
            INSERT INTO fichas (jogador_id, nome_personagem)
            VALUES (?, ?)
            """,
            (jogador_id, nome_personagem)
        )

        conexao.commit()
        conexao.close()

        return redirect("/jogador")

    return render_template("criar_ficha.html")

@app.route("/rolar-d4", methods=["POST"])
def rolar_d4():

    sala_id = session.get("sala_id")

    if sala_id is None:
        return "Você não está em nenhuma sala."

    conexao = conectar()

    # Verifica se é mestre
    token_mestre = session.get("token_mestre")

    if token_mestre is not None:

        sala = conexao.execute(
            """
            SELECT * FROM salas
            WHERE id = ? AND token_mestre = ?
            """,
            (sala_id, token_mestre)
        ).fetchone()

        if sala is None:
            conexao.close()
            return "Sessão de mestre inválida."

        jogador_id = None
        nome = sala["nome_mestre"]

    # Caso contrário, verifica se é jogador
    else:

        jogador_id = session.get("jogador_id")

        if jogador_id is None:
            conexao.close()
            return "Sessão inválida."

        jogador = conexao.execute(
            """
            SELECT * FROM jogadores
            WHERE id = ? AND sala_id = ?
            """,
            (jogador_id, sala_id)
        ).fetchone()

        if jogador is None:
            conexao.close()
            return "Jogador não encontrado."

        nome = jogador["nome"]

    # Gera o resultado do D4
    resultado = random.randint(1, 4)

    # Salva a rolagem
    conexao.execute(
        """
        INSERT INTO rolagens
        (sala_id, jogador_id, dado, resultado)
        VALUES (?, ?, ?, ?)
        """,
        (sala_id, jogador_id, "d4", resultado)
    )

    conexao.commit()
    conexao.close()

    # Envia a rolagem em tempo real para todos os usuários
    # que estão na mesma room (mesma sala).
    socketio.emit(
    "rolagem_dado",
    {
        "nome": nome,
        "dado": "d4",
        "resultado": resultado
    },
    room=str(sala_id)
)
    # envia json para o javascript
    return jsonify({
    "nome": nome,
    "dado": "d4",
    "resultado": resultado
})

# Escuta o evento "entrar_sala" enviado pelo JavaScript e executa esta função.
@socketio.on("entrar_sala")
def entrar_sala_socket():

    sala_id = session.get("sala_id")


    if sala_id is None:
        print("Usuário não possui sala.")
        return

    join_room(str(sala_id))

    print("Usuário entrou na room:", str(sala_id))


if __name__ == "__main__":
    # Inicia o Flask através do SocketIO para permitir comunicação em tempo real.
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)