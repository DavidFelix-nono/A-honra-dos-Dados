// Cria uma conexão com o servidor Socket.IO.
//
// "io()" vem da biblioteca Socket.IO que carregamos no HTML.
// É parecido com criar uma referência para um sistema que
// queremos utilizar.
const socket = io();


// Procura no HTML um elemento que tenha:
// id="botaoD4"
//
// document = representa a página HTML atual.
// getElementById = procura um elemento pelo seu ID.
//
// Em C#, pense nisso como procurar uma referência de um
// GameObject/Componente pelo nome/identificador.
const botaoD4 = document.getElementById("botaoD4");


// Procura no HTML o elemento:
// id="resultadoRolagem"
//
// Vamos usar esse elemento posteriormente para mostrar
// o resultado do dado na tela.
const resultadoRolagem = document.getElementById("resultadoRolagem");


// =====================================================
// CONEXÃO COM O SOCKET.IO
// =====================================================


// socket.on() significa:
//
// "Fique escutando um determinado evento."
//
// "connect" é um evento próprio do Socket.IO.
// Ele acontece automaticamente quando o navegador
// consegue estabelecer conexão com o servidor.
//
// function() { ... } é a função que será executada
// quando esse evento acontecer.
socket.on("connect", function () {


    // Mostra uma mensagem no console do navegador.
    //
    // console.log() é basicamente um Debug.Log() do Unity.
    console.log("Conectado ao Socket.IO.");


    // Envia um evento para o servidor.
    //
    // O nome do evento é "entrar_sala".
    //
    // No Python temos:
    //
    // @socketio.on("entrar_sala")
    //
    // Portanto, quando fazemos isso:
    //
    // socket.emit("entrar_sala")
    //
    // o Python recebe o evento e executa a função
    // associada a "entrar_sala".
    socket.emit("entrar_sala");
});


// =====================================================
// ROLAR D4
// =====================================================


// addEventListener() registra uma função que será executada
// quando alguma coisa acontecer com esse elemento.
//
// "click" significa:
// "quando o botão for clicado".
//
// Portanto:
// botão D4 foi clicado
//        ↓
// execute a função abaixo.
//
// async significa que essa função pode esperar operações
// que demoram algum tempo, usando "await".
botaoD4.addEventListener("click", async function () {


    // fetch() faz uma requisição para o servidor.
    //
    // Aqui estamos dizendo:
    //
    // "Faça uma requisição para /rolar-d4".
    //
    // É parecido com quando o Unity faz uma requisição
    // HTTP para um servidor.
    const resposta = await fetch("/rolar-d4", {


        // Dizemos que o método HTTP utilizado será POST.
        //
        // Portanto isso corresponde à nossa rota Flask:
        //
        // @app.route("/rolar-d4", methods=["POST"])
        method: "POST"
    });


    // resposta.ok verifica se o servidor respondeu
    // corretamente.
    //
    // Se houver um erro HTTP, entra nesse if.
    if (!resposta.ok) {


        // console.error() mostra um erro no console.
        //
        // É semelhante ao Debug.LogError() do Unity.
        console.error("Erro ao rolar o dado.");


        // "return" interrompe a execução da função.
        //
        // Ou seja:
        // ocorreu um erro → não continue.
        return;
    }


    // O servidor respondeu.
    //
    // Nossa rota Flask retorna:
    //
    // {
    //     "nome": "Lara",
    //     "dado": "d4",
    //     "resultado": 3
    // }
    //
    // resposta.json() transforma esse JSON recebido
    // em um objeto JavaScript.
    //
    // await significa:
    // "espere terminar de converter antes de continuar."
    const dados = await resposta.json();


    // Mostra no console os dados recebidos.
    //
    // "dados" agora contém algo como:
    //
    // dados.nome      → "Lara"
    // dados.dado      → "d4"
    // dados.resultado → 3
    console.log("Resultado recebido pela requisição:", dados);
});


// =====================================================
// RECEBER ROLAGEM DA SALA
// =====================================================


// Aqui estamos novamente usando socket.on(),
// portanto estamos dizendo:
//
// "Fique escutando um evento."
//
// O evento que queremos escutar se chama:
// "rolagem_dado"
//
// Esse é o mesmo nome usado no Python:
//
// socketio.emit("rolagem_dado", ...)
//
// Quando o servidor enviar esse evento,
// essa função será executada.
socket.on("rolagem_dado", function (dados) {


    // Mostra no console os dados enviados pelo servidor.
    //
    // Por exemplo:
    //
    // {
    //     nome: "Lara",
    //     dado: "d4",
    //     resultado: 3
    // }
    console.log("Rolagem recebida:", dados);


    // innerHTML permite alterar o conteúdo HTML
    // que está dentro de um elemento.
    //
    // Nossa variável resultadoRolagem aponta para:
    //
    // <div id="resultadoRolagem"></div>
    //
    // Então estamos colocando um <p> dentro desse div.
    resultadoRolagem.innerHTML = `


        // ${dados.nome}
        //
        // Pega o nome enviado pelo servidor.
        //
        // Se dados.nome for "Lara":
        //
        // ${dados.nome}
        //
        // vira:
        //
        // Lara
        <p>


            // dados.dado pega o tipo do dado.
            //
            // Nesse caso:
            // "d4"
            //
            // .toUpperCase() transforma letras minúsculas
            // em maiúsculas.
            //
            // "d4".toUpperCase()
            //       ↓
            // "D4"
            ${dados.nome} rolou ${dados.dado.toUpperCase()} → ${dados.resultado}


        </p>
    `;
});