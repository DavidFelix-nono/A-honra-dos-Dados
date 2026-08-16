from flask import Flask, render_template, request, redirect, session
from database import inicializar_banco, conectar
import secrets
import string

app = Flask(__name__)
app.secret_key = "chave-do-projeto"

inicializar_banco()


@app.route("/")
def inicio():
    return render_template("index.html")


@app.route("/criar-sala", methods=["GET", "POST"])
def criar_sala():

    if request.method == "POST":
        nome = request.form["nome"]

        caracteres = string.ascii_uppercase + string.digits
        codigo = "".join(secrets.choice(caracteres) for _ in range(5))

        token_mestre = secrets.token_hex(32)

        conexao = conectar()

        sala_id = conexao.execute(
            """
            INSERT INTO salas (codigo, nome, token_mestre)
            VALUES (?, ?, ?)
            """,
            (codigo, nome, token_mestre)
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


@app.route("/entrar-sala")
def entrar_sala():
    return "Página para entrar em sala"


@app.route("/mestre")
def mestre():
    sala_id = session.get("sala_id")

    if sala_id is None:
        return "Você não é mestre de nenhuma sala."

    conexao = conectar()

    sala = conexao.execute(
        "SELECT * FROM salas WHERE id = ?",
        (sala_id,)
    ).fetchone()

    conexao.close()

    if sala is None:
        return "Sala não encontrada."

    return render_template("mestre.html", sala=sala)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)