import React from "react";
import "./FloatingButton.css";

const FloatingButton = ({ onClick, startNewChat }) => {
    const handleClick = async () => {
        if (onClick) onClick();  // Alternar visibilidade do chatbot
        
        if (startNewChat) {
            try {
                await startNewChat(); // Chama a função de reset do chat
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
