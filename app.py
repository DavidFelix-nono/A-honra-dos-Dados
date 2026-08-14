from flask import Flask, render_template
from database import inicializar_banco

app = Flask(__name__)

inicializar_banco()


@app.route("/")
def inicio():
    return render_template("index.html")


@app.route("/criar-sala")
def criar_sala():
    return "Página para criar sala"


@app.route("/entrar-sala")
def entrar_sala():
    return "Página para entrar em sala"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)