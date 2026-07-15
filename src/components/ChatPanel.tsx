import { useEffect, useRef, useState, type FC, type FormEvent } from 'react';
import type { ChatMessage } from '../types';

interface ChatPanelProps {
  messages: ChatMessage[];
  quickCommands: string[];
  sending: boolean;
  onSend: (text: string) => void;
}

export const ChatPanel: FC<ChatPanelProps> = ({ messages, quickCommands, sending, onSend }) => {
  const [value, setValue] = useState('');
  const messagesContainerRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    const container = messagesContainerRef.current;
    if (!container) {
      return;
    }

    container.scrollTo({
      top: container.scrollHeight,
      behavior: 'smooth'
    });
  }, [messages]);

  const submitMessage = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();

    if (!value.trim()) {
      return;
    }

    onSend(value);
    setValue('');
  };

  return (
    <section className="chat-panel card">
      <div className="panel-header">
        <div>
          <p className="eyebrow">Quick Chat</p>
          <h3>AI 指令面板</h3>
        </div>
      </div>

      <div className="quick-command-list">
        {quickCommands.map((command) => (
          <button key={command} type="button" className="quick-command" onClick={() => onSend(command)}>
            {command}
          </button>
        ))}
      </div>

      <div ref={messagesContainerRef} className="chat-messages">
        {messages.map((message) => (
          <article
            key={message.id}
            className={`chat-message ${message.sender === 'user' ? 'chat-message-user' : 'chat-message-assistant'}`}
          >
            <strong>{message.sender === 'user' ? '你' : 'AI 员工'}</strong>
            <p>{message.text}</p>
            <span>{message.timestamp}</span>
          </article>
        ))}

        {sending ? (
          <article className="chat-message chat-message-assistant typing-message">
            <strong>AI 员工</strong>
            <p>正在分析指令并生成回复…</p>
          </article>
        ) : null}
      </div>

      <form className="chat-form" onSubmit={submitMessage}>
        <input
          type="text"
          value={value}
          onChange={(event) => setValue(event.target.value)}
          placeholder="输入 SAP 运营指令，例如：检查发票异常"
        />
        <button type="submit" disabled={sending}>
          发送
        </button>
      </form>
    </section>
  );
};
