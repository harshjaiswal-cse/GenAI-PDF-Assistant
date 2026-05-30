import { useState } from "react";
import api from "../services/api";

function ChatBox() {
  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState([]);

  const askQuestion = async () => {
    if (!question.trim()) return;

    try {
      const response = await api.get("/ask/", {
        params: {
          query: question,
        },
      });

      setMessages((prev) => [
        ...prev,
        {
          type: "user",
          text: question,
        },
        {
          type: "bot",
          text: response.data.answer,
        },
      ]);

      setQuestion("");
    } catch (error) {
      console.error("API Error:", error);
      alert("Error getting answer");
    }
  };

  return (
    <div className="chat-container">
      <div className="chat-header">
        🤖 GenAI PDF Assistant
      </div>

      <div className="messages">
        {messages.length === 0 && (
          <div className="bot-message">
            👋 Upload a PDF and ask questions.
          </div>
        )}

        {messages.map((msg, index) => (
          <div
            key={index}
            className={
              msg.type === "user"
                ? "user-message"
                : "bot-message"
            }
          >
            {msg.text}
          </div>
        ))}
      </div>

      <div className="input-area">
        <input
          type="text"
          value={question}
          placeholder="Ask anything from your PDF..."
          onChange={(e) => setQuestion(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter") {
              askQuestion();
            }
          }}
        />

        <button onClick={askQuestion}>
          Send
        </button>
      </div>
    </div>
  );
}

export default ChatBox;