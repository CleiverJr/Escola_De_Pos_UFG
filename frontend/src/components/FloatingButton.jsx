import React from "react";
import "./FloatingButton.css";
import axios from 'axios';

const FloatingButton = ({ onClick, startNewChat }) => {
    const handleClick = async () => {
        if (onClick) onClick();  // Alternar visibilidade do chatbot
    
        // Verifica se já existe um chat_id no localStorage
        let chat_id = localStorage.getItem('chat_id');
    
        // Se não houver chat_id, inicia um novo chat
        if (!chat_id) {
            try {
                const response = await axios.get("http://127.0.0.1:8000/api/new_chat");
                chat_id = response.data.chat_id;
                localStorage.setItem('chat_id', chat_id);  // Salva o novo chat_id
            } catch (error) {
                console.error("Erro ao iniciar novo chat:", error);
            }
        }
    };    

    return (
        <button className="floating-button" onClick={handleClick}>
            💬
        </button>
    );
};

export default FloatingButton;
