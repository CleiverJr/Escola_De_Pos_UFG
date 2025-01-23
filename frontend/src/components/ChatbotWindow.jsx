import React, { useState, useEffect } from 'react';
import axios from 'axios';
import FloatingButton from './FloatingButton';
import './ChatbotWindow.css';

const ChatbotWindow = () => {
    const [isOpen, setIsOpen] = useState(false);
    const [messages, setMessages] = useState([]);
    const [userMessage, setUserMessage] = useState('');
    const [typingMessage, setTypingMessage] = useState(''); // Estado para mensagem digitada
    const [isTyping, setIsTyping] = useState(false); // Controla se o bot está "digitando"

    const toggleChatbot = () => {
        setIsOpen(!isOpen);
    };

    const sendMessage = async () => {
        if (!userMessage.trim()) return;

        const currentTime = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

        // Adiciona mensagem do usuário
        setMessages([...messages, { sender: 'user', text: userMessage, time: currentTime }]);

        try {
            // Faz a requisição para a API
            const response = await axios.post('http://127.0.0.1:8000/api/chat', {
            query: userMessage,
        });

            const botReply = response.data.reply || 'Resposta padrão do bot';

            // Adiciona animação de digitação
            simulateTyping(botReply);
        } catch (error) {
            console.error('Erro ao chamar a API:', error);

            simulateTyping('Erro ao obter resposta. Tente novamente.');
        }

        setUserMessage('');
    };

    // Função para simular a digitação do bot
    const simulateTyping = (text) => {
        setIsTyping(true);
        setTypingMessage(''); // Reinicia o texto digitado
        const words = text.split(' '); // Divide o texto em palavras
        let index = -1;

        const botTime = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }); // Horário atual

        const interval = setInterval(() => {
            setTypingMessage((prev) => (prev + (prev ? ' ' : '') + words[index])); // Adiciona palavra por palavra
            index++;

            if (index === words.length) {
                clearInterval(interval);
                setIsTyping(false);

                // Quando a digitação termina, adiciona a mensagem final ao histórico com o horário
                setMessages((prev) => [
                    ...prev,
                    { sender: 'bot', text: text, time: botTime },
                ]);
                setTypingMessage(''); // Limpa o texto temporário
            }
        }, 100); // Velocidade da digitação (300ms por palavra)
    };



    return (
        <>
            <FloatingButton onClick={toggleChatbot} />

            <div className={`chatbot-container ${isOpen ? 'visible' : ''}`}>
                <div className="chatbot-header">Chatbot</div>
                <div className="chatbot-messages">
                    {messages.map((message, index) => (
                        <div
                            key={index}
                            style={{
                                textAlign: message.sender === 'user' ? 'right' : 'left',
                                marginBottom: '10px',
                            }}
                        >
                            <div>
                                <strong>{message.sender === 'user' ? 'Você' : 'Bot'}:</strong> {message.text}
                            </div>
                            <div
                                style={{
                                    fontSize: '0.8em',
                                    color: 'gray',
                                    marginTop: '5px',
                                }}
                            >
                                {message.time}
                            </div>
                        </div>
                    ))}

                    {/* Exibe a mensagem temporária sendo digitada */}
                    {isTyping && (
                        <div style={{ textAlign: 'left', marginBottom: '10px' }}>
                            <div>
                                <strong>Bot:</strong> {typingMessage}
                            </div>
                            <div
                                style={{
                                    fontSize: '0.8em',
                                    color: 'gray',
                                    marginTop: '5px',
                                }}
                            >
                                {new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                            </div>
                        </div>
                    )}
                </div>

                <div className="chatbot-input-container">
                    <input
                        className="chatbot-input"
                        type="text"
                        value={userMessage}
                        onChange={(e) => setUserMessage(e.target.value)}
                        placeholder="Digite sua mensagem..."
                    />
                    <button className="chatbot-button" onClick={sendMessage}>
                        Enviar
                    </button>
                </div>
            </div>
        </>
    );
};

export default ChatbotWindow;
