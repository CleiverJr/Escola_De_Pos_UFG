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
    const messagesEndRef = useRef(null); // Ref para rolar até o final automaticamente
    const warningSentRef = useRef(false);  // Para garantir que a mensagem de aviso só seja enviada uma vez

    const toggleChatbot = async () => {
        setIsOpen((prev) => !prev);

        if (!isOpen) {
            await startNewChat(); // Inicia o chat ao abrir
        }
    };

    const startNewChat = async () => {
        try {
            let chat_id = sessionStorage.getItem('chat_id');

            if (!chat_id) {
                const response = await axios.get("http://127.0.0.1:8000/api/new_chat");
                chat_id = response.data.chat_id;
                sessionStorage.setItem('chat_id', chat_id);

                // Se houver uma mensagem de boas-vindas do backend, usa simulateTyping
                if (response.data.bot_reply) {
                    simulateTyping(response.data.bot_reply.text);
                }
            }
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
        setTypingMessage('');
        const words = text.split(' ');
        let index = 0;

        const botTime = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

        const interval = setInterval(() => {
            setTypingMessage((prev) => (prev + (prev ? ' ' : '') + words[index]));
            index++;

            if (index === words.length) {
                clearInterval(interval);
                setIsTyping(false);

                setMessages((prev) => [
                    ...prev,
                    { sender: 'bot', text: text, time: botTime },
                ]);
                setTypingMessage('');
            }
        }, 100);
    };

    const handleKeyPress = (event) => {
        if (event.key === 'Enter') {
            sendMessage();
        }
    };

    const formatMessageWithLinks = (text) => {
        const urlRegex = /(https?:\/\/[^\s]+)/g;
        return text.split(urlRegex).map((part, index) => 
            urlRegex.test(part) ? (
                <a key={index} href={part} target="_blank" rel="noopener noreferrer" style={{ color: 'blue' }}>
                    {part}
                </a>
            ) : (
                part
            )
        );
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
    
    // Função para rolar automaticamente até o final
    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    // Efeito para rolar sempre que uma nova mensagem for adicionada
    useEffect(() => {
        scrollToBottom();
    }, [messages, typingMessage]);


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
            <FloatingButton onClick={toggleChatbot} startNewChat={startNewChat} setMessages={setMessages} />

            <div className={`chatbot-container ${isOpen ? 'visible' : ''}`}>
                <div className="chatbot-header">Chatbot</div>
                <div className="chatbot-messages">
                    {messages.map((message, index) => (
                        <div key={index} style={{ textAlign: message.sender === 'user' ? 'right' : 'left', marginBottom: '10px' }}>
                            <div>
                                <strong>{message.sender === 'user' ? 'Você' : 'Ana'}:</strong> {message.sender === 'bot' ? formatMessageWithLinks(message.text) : message.text}
                            </div>
                            <div style={{ fontSize: '0.8em', color: 'gray', marginTop: '5px' }}>
                                {message.time}
                            </div>
                        </div>
                    ))}

                    {/* Exibe a mensagem temporária sendo digitada */}
                    {isTyping && (
                        <div style={{ textAlign: 'left', marginBottom: '10px' }}>
                            <div> 
                                <strong>Ana:</strong> {typingMessage}
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

                    <div ref={messagesEndRef} />
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