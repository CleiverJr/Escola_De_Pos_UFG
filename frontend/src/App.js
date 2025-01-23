import React, { useState } from "react";
import FloatingButton from "./components/FloatingButton";
import ChatbotWindow from "./components/ChatbotWindow";

const App = () => {
  const [isChatVisible, setChatVisible] = useState(false);

  const toggleChat = () => {
    setChatVisible(!isChatVisible);
  };

  return (
    <div>
      <ChatbotWindow isVisible={isChatVisible} onClose={toggleChat} />
    </div>
  );
};

export default App;
