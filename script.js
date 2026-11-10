
// Conexão MQTT do Dashboard
var broker = "broker.hivemq.com";
var clientId = "cartografo_g18_" + Math.random().toString(16).slice(2, 10);

var TOPICO_INFECCAO = "cscf/grupo18/hollow/templo/infeccao";
var TOPICO_COMANDO_TEMPLO = "cscf/grupo18/hollow/templo/comando";
var TOPICO_COMANDO_BESOURO = "cscf/grupo18/hollow/estacao/comando";
var TOPICO_CHAMADO = "cscf/grupo18/hollow/estacao/chamado";
var TOPICO_ESTADO_BANCO = "cscf/grupo18/hollow/banco/estado";
var TOPICO_COMANDO_BANCO = "cscf/grupo18/hollow/banco/comando";

var client = new Paho.MQTT.Client(broker, 8000, clientId);

var connectionStatus = document.getElementById("connection-status");
var connectionIndicator = document.getElementById("connection-indicator");

// Atualiza o indicador de conexão.
function atualizarConexao(conectado, texto) {
    connectionStatus.innerText = texto;
    connectionIndicator.classList.toggle("is-connected", conectado);
    connectionIndicator.classList.toggle("is-disconnected", !conectado);
}

// Detecta a perda da conexão MQTT.
client.onConnectionLost = function(responseObject) {
    if (responseObject.errorCode !== 0) {
        console.log("Conexão MQTT perdida: " + responseObject.errorMessage);
        atualizarConexao(false, "Conexão MQTT perdida");
    }
};

// Recebe e processa as mensagens MQTT.
client.onMessageArrived = function(message) {
    var topico = message.destinationName;
    var payload = message.payloadString;

    if (topico === TOPICO_INFECCAO) {
        var statusInfeccao = document.getElementById("status-infeccao");

        statusInfeccao.innerText = payload;
        statusInfeccao.className = "status " +
            (payload === "ALTA" ? "status-danger" : "status-good");

    } else if (topico === TOPICO_ESTADO_BANCO) {
        var statusBanco = document.getElementById("status-banco");

        statusBanco.innerText = payload;
        statusBanco.className = "status " +
            (payload === "OCUPADO" ? "status-warning" : "status-good");

    } else if (topico === TOPICO_CHAMADO && payload === "TRUE") {
        var statusBesouro = document.getElementById("status-besouro");

        statusBesouro.innerText = "BESOURO A CAMINHO";
        statusBesouro.className = "status status-info";

        window.setTimeout(function() {
            if (statusBesouro.innerText === "BESOURO A CAMINHO") {
                statusBesouro.innerText = "Aguardando chamado...";
                statusBesouro.className = "status";
            }
        }, 4000);
    }
};

// Conecta ao broker HiveMQ.
client.connect({
    useSSL: false,

    onSuccess: function() {
        console.log("Mesa do Cartógrafo conectada ao HiveMQ.");
        atualizarConexao(true, "Conectado ao broker MQTT");

        client.subscribe(TOPICO_INFECCAO);
        client.subscribe(TOPICO_ESTADO_BANCO);
        client.subscribe(TOPICO_CHAMADO);
    },

    onFailure: function(error) {
        console.log("Falha na conexão MQTT: " + error.errorMessage);
        atualizarConexao(false, "Não foi possível conectar ao MQTT");
    }
});

// Publica uma mensagem em um tópico MQTT.
function enviarMensagem(topico, payload) {
    if (!client.isConnected()) {
        console.warn("Comando não enviado: Dashboard sem conexão MQTT.");
        return false;
    }

    var mensagem = new Paho.MQTT.Message(payload);
    mensagem.destinationName = topico;

    client.send(mensagem);
    return true;
}

// Controle remoto do LED do Sistema A.
function controlarLedTemplo(comando) {
    var feedback = document.getElementById("status-comando-templo");

    if (enviarMensagem(TOPICO_COMANDO_TEMPLO, comando)) {
        var mensagens = {
            LIGAR: "Comando enviado: ligar LED.",
            DESLIGAR: "Comando enviado: desligar LED.",
            AUTO: "Comando enviado: voltar ao modo automático."
        };

        feedback.innerText = mensagens[comando];
    } else {
        feedback.innerText = "Sem conexão MQTT. Tente novamente em instantes.";
    }
}

// Controle remoto do portão do Sistema B.
function controlarPortao(comando) {
    var feedback = document.getElementById("status-comando-besouro");

    if (enviarMensagem(TOPICO_COMANDO_BESOURO, comando)) {
        var mensagens = {
            ABRIR: "Comando enviado: abrir portão.",
            FECHAR: "Comando enviado: fechar portão.",
            AUTO: "Comando enviado: voltar ao modo automático."
        };

        feedback.innerText = mensagens[comando];
    } else {
        feedback.innerText = "Sem conexão MQTT. Tente novamente em instantes.";
    }
}

// Solicita o Besouro; o Sistema C recebe o chamado e pisca o LED.
function chamarBesouro() {
    if (!enviarMensagem(TOPICO_CHAMADO, "TRUE")) {
        document.getElementById("status-besouro").innerText = "Sem conexão MQTT";
    }
}

// Controle remoto do LED do Sistema C.
function controlarLedBanco(comando) {
    var feedback = document.getElementById("status-comando-banco");

    if (enviarMensagem(TOPICO_COMANDO_BANCO, comando)) {
        var mensagens = {
            LIGAR: "Comando enviado: ligar LED.",
            DESLIGAR: "Comando enviado: desligar LED.",
            AUTO: "Comando enviado: voltar ao modo automático."
        };

        feedback.innerText = mensagens[comando];
    } else {
        feedback.innerText = "Sem conexão MQTT. Tente novamente em instantes.";
    }
}
