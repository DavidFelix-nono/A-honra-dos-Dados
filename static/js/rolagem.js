const socket = io();

const botaoD4 = document.getElementById("botaoD4");
const resultadoRolagem = document.getElementById("resultadoRolagem");


// =====================================================
// CONEXÃO COM O SOCKET.IO
// =====================================================

socket.on("connect", function () {

    console.log("Conectado ao Socket.IO.");

    // Informa ao servidor que este usuário entrou na sala.
    socket.emit("entrar_sala");
});


// =====================================================
// ROLAR D4
// =====================================================

if (botaoD4) {

    botaoD4.addEventListener("click", async function () {

        console.log("Botão D4 clicado.");

        try {

            const resposta = await fetch("/rolar-d4", {
                method: "POST"
            });

            if (!resposta.ok) {

                console.error(
                    "Erro ao rolar o dado:",
                    resposta.status
                );

                return;
            }

            const dados = await resposta.json();

            console.log(
                "Resultado recebido pela requisição:",
                dados
            );

        } catch (erro) {

            console.error(
                "Erro na comunicação com o servidor:",
                erro
            );
        }
    });
}


// =====================================================
// RECEBER ROLAGEM DA SALA
// =====================================================

socket.on("rolagem_dado", function (dados) {

    console.log("Rolagem recebida:", dados);

    // Cria um novo elemento <p>
    const novaRolagem = document.createElement("p");

    // Define o texto que será exibido
    novaRolagem.textContent =
        `${dados.nome} rolou ${dados.dado.toUpperCase()} → ${dados.resultado}`;

    // Adiciona a nova rolagem ao histórico
    resultadoRolagem.appendChild(novaRolagem);
});