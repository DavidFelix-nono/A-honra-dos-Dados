from flask import Flask, render_template, request, redirect
from database import inicializar_banco, conectar
import secrets
import string

app = Flask(__name__)

inicializar_banco()


@app.route("/")
def inicio():
    return render_template("index.html")


@app.route("/criar-sala", methods=["GET", "POST"])
def criar_sala():

    if request.method == "POST":
        nome = request.form["nome"]

        caracteres = string.ascii_uppercase + string.digits # Gera um conjunto de caracteres que inclui letras maiúsculas e números
        codigo = "".join(secrets.choice(caracteres) for _ in range(5)) # Gera um código aleatório de 5 caracteres (letras maiúsculas e números)

        token_mestre = secrets.token_hex(32) # Gera um token aleatório de 32 caracteres

        conexao = conectar()

        conexao.execute(
            """
            INSERT INTO salas (codigo, nome, token_mestre)
            VALUES (?, ?, ?)
            """,
            (codigo, nome, token_mestre)
        )

        conexao.commit()
        conexao.close()

        return f"Sala criada! Código: {codigo}"

    return render_template("criar_sala.html")


@app.route("/entrar-sala")
def entrar_sala():
    return "Página para entrar em sala"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)