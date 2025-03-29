let websocket;

const statusElement = document.getElementById("status");
const messageElement = document.getElementById("message");
const userMessageElement = document.getElementById("userMessage");

document.getElementById("connect").addEventListener("click", () => {
    websocket = new WebSocket("ws://127.0.0.1:8000/ws");
    websocket.onopen = () => { // 웹 소켓 연결 성공
        statusElement.innerText = "Connected";
        document.getElementById("connect").disabled = true;
        document.getElementById("disconnect").disabled = false;
    };
    websocket.onmessage = (event) => { // 서버로부터 메시지를 받았을 때
        const newMessage = document.createElement("p");
        newMessage.innerText = `Received: ${event.data}`;
        messageElement.appendChild(newMessage);
    };
    websocket.onclose = () => { // 웹 소켓 연결 해제
        statusElement.innerText = "Disconnected";
        document.getElementById("connect").disabled = false;
        document.getElementById("disconnect").disabled = true;
    };
});

document.getElementById("disconnect").addEventListener("click", () => {
    websocket.close();
});

document.getElementById("sendMessage").addEventListener("click", () => {
    const message = userMessageElement.value;
    websocket.send(message);

    const sentMessage = document.createElement("p");
    sentMessage.innerText = `Sent: ${message}`;
    messageElement.appendChild(sentMessage);
});