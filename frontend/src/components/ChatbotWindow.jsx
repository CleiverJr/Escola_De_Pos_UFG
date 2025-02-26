import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import FloatingButton from './FloatingButton';
import './ChatbotWindow.css';

const ChatbotWindow = () => {
    const [isOpen, setIsOpen] = useState(false);
    const [messages, setMessages] = useState([]);
    const [userMessage, setUserMessage] = useState('');
    const [typingMessage, setTypingMessage] = useState(''); // Estado para mensagem digitada
    const [isTyping, setIsTyping] = useState(false); // Controla se o bot está "digitando"
    const inactivityTimerRef = useRef(null);  // Ref para o timer de inatividade
    const warningSentRef = useRef(false);  // Para garantir que a mensagem de aviso só seja enviada uma vez

    const toggleChatbot = () => {
        setIsOpen(!isOpen);
    };

    const startNewChat = async () => {
        try {
            const response = await axios.get("http://127.0.0.1:8000/api/new_chat");
            const { chat_id } = response.data;
            
            // Armazena o chat_id no sessionStorage
            sessionStorage.setItem('chat_id', chat_id);
    
            console.log(response.data);
        } catch (error) {
            console.error("Erro ao iniciar novo chat:", error);
        }
    };
    
    
    

    const sendMessage = async () => {
        if (!userMessage.trim()) return;
    
        const currentUserMessage = userMessage;
        setUserMessage('');
    
        const currentTime = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        setMessages([...messages, { sender: 'user', text: currentUserMessage, time: currentTime }]);

        resetInactivityTimer();  // Reinicia o timer de inatividade após envio de mensagem
    
        try {
            let chat_id = sessionStorage.getItem('chat_id');
    
            // Se não houver chat_id, inicia um novo chat
            if (!chat_id) {
                await startNewChat();
                chat_id = sessionStorage.getItem('chat_id');
            }
    
            const response = await axios.post('http://127.0.0.1:8000/api/chat', {
                query: currentUserMessage,
                chat_id: chat_id,  // Envia o chat_id para o backend
            });
    
            const botReply = response.data.reply || 'Resposta padrão do bot';
            simulateTyping(botReply);
        } catch (error) {
            console.error('Erro ao chamar a API:', error);
            simulateTyping('Erro ao obter resposta. Tente novamente.');
        }
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

    const handleKeyPress = (event) => {
        if (event.key === 'Enter') {
            sendMessage();
        }
    };

    const resetInactivityTimer = () => {
        clearTimeout(inactivityTimerRef.current);
        warningSentRef.current = false;

        inactivityTimerRef.current = setTimeout(() => {
            if (!warningSentRef.current) {
                sendBotMessage("Você ainda está aí?");
                warningSentRef.current = true;
                
                // Inicia o temporizador para encerrar o chat após 5 minutos adicionais (10 minutos no total)
                inactivityTimerRef.current = setTimeout(() => {
                    sendBotMessage("O chat foi encerrado devido à inatividade. Inicie uma nova conversa quando quiser!");
                    endChat();
                }, 5 * 60 * 1000);  // 5 minutos adicionais
            }
        }, 5 * 60 * 1000);  // Primeiro aviso após 5 minutos
    };

    const endChat = () => {
        const chatId = sessionStorage.getItem('chat_id');
        console.log('Encerrando chat com chat_id:', chatId);  // Verifique se o chat_id está correto
    
        if (!chatId) {
            console.error('chat_id não encontrado. O chat já pode estar encerrado.');
            return;
        }
    
        sessionStorage.removeItem('chat_id');
        
    
        axios.post('http://127.0.0.1:8000/api/end_chat', {
            query: "encerrar_chat",  // Indicando que a ação é para encerrar o chat
            chat_id: chatId
        })
        .then(response => {
            console.log('Chat encerrado com sucesso:', response.data);
        })
        .catch(error => {
            console.error('Erro ao encerrar o chat:', error);
        });
        
    };
    

    const sendBotMessage = (text) => {
        const botTime = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        setMessages((prev) => [...prev, { sender: 'bot', text, time: botTime }]);
    };

    useEffect(() => {
        if (isOpen) {
            resetInactivityTimer();  // Inicia o timer quando o chat é aberto
        } else {
            clearTimeout(inactivityTimerRef.current);  // Limpa o timer se o chat for fechado
        }
    }, [isOpen]);

    return (
        <>
            <FloatingButton onClick={toggleChatbot} startNewChat={startNewChat} />

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
                        onKeyDown={handleKeyPress} // Adicionado para detectar a tecla Enter
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
