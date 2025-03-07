import React, { useState, useEffect, useCallback, useRef } from 'react';
import Doodle from './assets/doodle.svg';
import ReactMarkdown from 'react-markdown';
import { REACT_APP_API_BASE_URL, SECRET_KEY_FOR_API } from './config';
import CryptoJS from 'crypto-js';
import { v4 as uuidv4 } from 'uuid';

function generateHMACSignature(secretKey, message) {
  return 'sha256=' + CryptoJS.HmacSHA256(message, secretKey).toString(CryptoJS.enc.Hex);
}

// Debounce function to delay the execution of a function
const debounce = (func, delay) => {
  let timeoutId;
  return (...args) => {
    if (timeoutId) {
      clearTimeout(timeoutId);
    }
    timeoutId = setTimeout(() => {
      func(...args);
    }, delay);
  };
};

function SearchComponent() {
  const [keyword, setKeyword] = useState('');
  const [results, setResults] = useState([]);
  const [chatMode, setChatMode] = useState(false);
  const [chatHistory, setChatHistory] = useState([]);
  const [isTyping, setIsTyping] = useState(false); // NEW: for showing spinner / “typing” state
  const messagesEndRef = useRef(null);

  // For the animated placeholder
  const placeholderTexts = [
    'Transformers..',
    'Query Rewriting..',
    'Late Chunking Methods',
    'Agentic Systems',
  ];
  const [placeholder, setPlaceholder] = useState('');

  const handleSearch = async (searchTerm) => {
    const requestId = uuidv4();
    if (searchTerm.length < 3) {
      setResults([]);
      return;
    }
    try {
      const apiUrl = REACT_APP_API_BASE_URL || 'http://localhost:8001';
      const hmacSignature = generateHMACSignature(SECRET_KEY_FOR_API, '');
      const response = await fetch(
        `${apiUrl}/api/v1/keyword_search?keyword=${encodeURIComponent(searchTerm)}&collection_name=LLM-gym`,
        {
          headers: {
            'X-Hub-Signature-256': hmacSignature,
            'X-Request-ID': requestId,
          },
        }
      );
      if (!response.ok) {
        console.error(`HTTP error! status: ${response.status}`);
        const errorText = await response.text();
        console.error('Response text:', errorText);
        setResults([]);
        return;
      }
      const data = await response.json();
      setResults(data.hits || []);
    } catch (error) {
      console.error('Error fetching data:', error);
      setResults([]);
    }
  };

  const debouncedSearch = useCallback(debounce(handleSearch, 200), []);

  useEffect(() => {
    if (!chatMode) {
      debouncedSearch(keyword);
    }
  }, [keyword, debouncedSearch, chatMode]);

  // Animated placeholder effect
  useEffect(() => {
    let index = 0; // Which word we're on
    let isDeleting = false;
    let currentText = '';
    let timerId;

    function type() {
      const word = placeholderTexts[index];

      if (!isDeleting) {
        currentText = word.substring(0, currentText.length + 1);
      } else {
        currentText = word.substring(0, currentText.length - 1);
      }

      setPlaceholder(currentText);

      // Adjust speed or “pause” as needed
      let nextDelay = 200;
      if (isDeleting) {
        nextDelay = 100; // deletion can be faster
      }

      if (!isDeleting && currentText === word) {
        // Pause at the full word
        nextDelay = 1000;
        isDeleting = true;
      } else if (isDeleting && currentText === '') {
        // Word completely deleted, move to next
        isDeleting = false;
        index = (index + 1) % placeholderTexts.length;
        nextDelay = 500;
      }
      timerId = setTimeout(type, nextDelay);
    }

    type();
    return () => clearTimeout(timerId);
  }, []);

  const handleChat = async (message) => {
    const requestId = uuidv4();
    if (!message.trim()) return;

    // Add the user's message to the chat history
    setChatHistory((prev) => [...prev, { content: message, role: 'user' }]);
    setKeyword(''); // Clear the input field
    setIsTyping(true); // Start “typing” indicator

    try {
      const apiUrl = REACT_APP_API_BASE_URL || 'http://localhost:8001';
      const body = JSON.stringify({
        messages: [
          ...chatHistory.filter((msg) => msg.role !== 'error'),
          { content: message, role: 'user' },
        ],
        collection_name: 'LLM-gym',
      });
      const hmacSignature = generateHMACSignature(SECRET_KEY_FOR_API, body);
      const response = await fetch(`${apiUrl}/api/v1/contextual_chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Hub-Signature-256': hmacSignature,
          'X-Request-ID': requestId,
        },
        body,
      });

      if (!response.ok) {
        console.error(`HTTP error! status: ${response.status}`);
        const errorText = await response.text();
        console.error('Response text:', errorText);
        setChatHistory((prev) => [
          ...prev,
          { content: 'Error fetching response.', role: 'error' },
        ]);
        setIsTyping(false);
        return;
      }
      const data = await response.json();

      // Extract content and citations
      const assistantMessage = {
        content: data.data.content,
        role: data.data.role,
        citations: data.meta?.citations || [],
      };

      setChatHistory((prev) => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Error fetching data:', error);
      setChatHistory((prev) => [
        ...prev,
        { content: 'Error fetching response.', role: 'error' },
      ]);
    } finally {
      setIsTyping(false); // Stop “typing” indicator
    }
  };

  // Scroll to bottom when new messages are added
  useEffect(() => {
    if (chatMode && messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [chatHistory, chatMode]);

  return (
    <div
      style={{
        position: 'relative',
        display: 'flex',
        flexDirection: 'column',
        minHeight: '100vh',
        background: 'linear-gradient(135deg, #a8c0ff, #3f2b96)',
        color: '#333',
        fontFamily: 'Arial, sans-serif',
        alignItems: 'center',
        padding: '20px',
      }}
    >
      {/* Toggle Switch in Top Right Corner */}
      <div
        style={{
          position: 'fixed',
          top: '20px',
          right: '20px',
          zIndex: 1000,
          backgroundColor: 'rgba(255, 255, 255, 0.8)',
          padding: '10px',
          borderRadius: '20px',
          boxShadow: '0 2px 4px rgba(0, 0, 0, 0.1)',
        }}
      >
        <label style={{ display: 'flex', alignItems: 'center', cursor: 'pointer' }}>
          <span style={{ marginRight: '8px', color: '#3f2b96' }}>
            {chatMode ? 'Chat Mode' : 'Search Mode'}
          </span>
          <div
            style={{
              position: 'relative',
              width: '50px',
              height: '24px',
            }}
          >
            <input
              type="checkbox"
              checked={chatMode}
              onChange={() => setChatMode(!chatMode)}
              style={{
                opacity: 0,
                width: 0,
                height: 0,
              }}
            />
            <span
              style={{
                position: 'absolute',
                top: 0,
                left: 0,
                right: 0,
                bottom: 0,
                backgroundColor: chatMode ? '#3f2b96' : '#ccc',
                borderRadius: '34px',
                transition: 'background-color 0.2s',
              }}
            ></span>
            <span
              style={{
                position: 'absolute',
                content: '""',
                top: '2px',
                left: chatMode ? '26px' : '2px',
                width: '20px',
                height: '20px',
                borderRadius: '50%',
                backgroundColor: '#fff',
                transition: 'left 0.2s',
                boxShadow: '0 2px 4px rgba(0, 0, 0, 0.2)',
              }}
            ></span>
          </div>
        </label>
      </div>

      {/* Logo */}
      <img
        src={Doodle}
        alt="LLM-gym Doodle"
        style={{ marginBottom: '20px', width: '150px' }}
      />

      {/* Search Bar */}
      {!chatMode && (
        <>
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              backgroundColor: '#3f2b96',
              borderRadius: '25px',
              boxShadow: '0 4px 12px rgba(0, 0, 0, 0.5)',
              padding: '10px 20px',
              width: '60%',
              maxWidth: '600px',
              transition: 'box-shadow 0.3s ease',
            }}
          >
            <input
              type="text"
              value={keyword}
              onChange={(e) => setKeyword(e.target.value)}
              placeholder={placeholder}
              style={{
                flex: 1,
                border: 'none',
                outline: 'none',
                fontSize: '16px',
                padding: '10px',
                backgroundColor: 'transparent',
                color: '#ffffff',
                marginRight: '10px',
              }}
            />
            <button
              onClick={() => handleSearch(keyword)}
              style={{
                padding: '10px 20px',
                cursor: 'pointer',
                backgroundColor: '#ffffff',
                color: '#3f2b96',
                border: 'none',
                borderRadius: '20px',
                boxShadow: '0 2px 4px rgba(0, 0, 0, 0.3)',
                transition: 'background-color 0.3s ease',
              }}
            >
              Search
            </button>
          </div>

          <div style={{ height: '40px' }}></div>
        </>
      )}

      {/* Content */}
      {chatMode ? (
        // Chat Mode UI
        <div
          style={{
            flex: 1,
            display: 'flex',
            flexDirection: 'column',
            width: '80%',
            maxWidth: '800px',
            overflowY: 'hidden',
            position: 'relative',
          }}
        >
          {/* Chat Messages */}
          <div
            style={{
              flex: 1,
              overflowY: 'auto',
              marginBottom: '70px',
              paddingRight: '10px',
            }}
          >
            {chatHistory.map((message, index) => (
              <div
                key={index}
                style={{
                  display: 'flex',
                  justifyContent: message.role === 'user' ? 'flex-end' : 'flex-start',
                  marginBottom: '10px',
                }}
              >
                <div
                  style={{
                    display: 'inline-block',
                    backgroundColor:
                      message.role === 'user'
                        ? '#3f2b96'
                        : message.role === 'error'
                        ? '#ffd7d7'
                        : 'rgba(255, 255, 255, 0.8)',
                    color:
                      message.role === 'user'
                        ? '#ffffff'
                        : message.role === 'error'
                        ? '#333'
                        : '#333333',
                    borderRadius: '20px',
                    padding: '15px',
                    maxWidth: '70%',
                    boxShadow: '0 2px 4px rgba(0, 0, 0, 0.1)',
                    wordWrap: 'break-word',
                    whiteSpace: 'pre-wrap',
                  }}
                >
                  <ReactMarkdown
                    components={{
                      pre: ({ node, ...props }) => (
                        <pre
                          {...props}
                          style={{
                            whiteSpace: 'pre-wrap',
                            wordWrap: 'break-word',
                            overflowWrap: 'break-word',
                            fontSize: '13px',
                            backgroundColor: '#f5f5f5',
                            padding: '10px',
                            borderRadius: '5px',
                            overflowX: 'auto',
                            marginTop: '8px',
                          }}
                        />
                      ),
                      code: ({ inline, children, ...props }) => (
                        <code
                          {...props}
                          style={{
                            whiteSpace: 'pre-wrap',
                            wordWrap: 'break-word',
                            overflowWrap: 'break-word',
                            fontSize: '13px',
                            backgroundColor: inline ? '#f5f5f5' : 'transparent',
                            padding: inline ? '2px 4px' : '0',
                            borderRadius: '3px',
                          }}
                        >
                          {children}
                        </code>
                      ),
                    }}
                  >
                    {message.content}
                  </ReactMarkdown>

                  {/* Display citations if available (only for assistant messages) */}
                  {message.citations && message.citations.length > 0 && (
                    <div style={{ marginTop: '10px', fontSize: '14px' }}>
                      <strong style={{ color: '#3f2b96' }}>Citations:</strong>
                      {message.citations.map((citation, i) => (
                        <div key={i}>
                          <a
                            href={citation}
                            style={{ color: '#3f2b96', textDecoration: 'underline' }}
                            target="_blank"
                            rel="noopener noreferrer"
                          >
                            {citation}
                          </a>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            ))}

            {/* “Assistant is typing” indicator */}
            {isTyping && (
              <div
                style={{
                  display: 'flex',
                  justifyContent: 'flex-start',
                  marginBottom: '10px',
                }}
              >
                <div
                  style={{
                    display: 'inline-block',
                    backgroundColor: 'rgba(255, 255, 255, 0.8)',
                    color: '#333333',
                    borderRadius: '20px',
                    padding: '15px',
                    maxWidth: '70%',
                    boxShadow: '0 2px 4px rgba(0, 0, 0, 0.1)',
                    fontStyle: 'italic',
                  }}
                >
                  Assistant is typing...
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Fixed Input Field */}
          <div
            style={{
              position: 'fixed',
              bottom: '20px',
              width: '80%',
              maxWidth: '800px',
              display: 'flex',
              alignItems: 'center',
            }}
          >
            <input
              type="text"
              value={keyword}
              onChange={(e) => setKeyword(e.target.value)}
              placeholder="Type your message..."
              onKeyPress={(e) => {
                if (e.key === 'Enter') {
                  handleChat(keyword);
                }
              }}
              style={{
                flex: 1,
                border: '1px solid #ccc',
                borderRadius: '20px',
                padding: '10px 15px',
                fontSize: '16px',
                marginRight: '10px',
                outline: 'none',
                backgroundColor: 'rgba(255, 255, 255, 0.9)',
              }}
            />
            <button
              onClick={() => handleChat(keyword)}
              style={{
                padding: '10px 20px',
                cursor: 'pointer',
                backgroundColor: '#3f2b96',
                color: '#ffffff',
                border: 'none',
                borderRadius: '20px',
              }}
              disabled={isTyping} // optional: prevent multiple rapid sends
            >
              {isTyping ? '...' : 'Send'}
            </button>
          </div>
        </div>
      ) : (
        // Search Mode UI
        <div
          style={{
            width: '80%',
            maxWidth: '800px',
            overflowY: 'auto',
            paddingBottom: '20px',
          }}
        >
          {results.map((result, index) => (
            <div
              key={index}
              style={{
                marginBottom: '20px',
                borderBottom: '1px solid rgba(255, 255, 255, 0.5)',
                paddingBottom: '10px',
                color: '#ffffff',
              }}
            >
              <a
                href={result.parent_link}
                style={{
                  textDecoration: 'none',
                  color: '#3f2b96',
                  fontSize: '18px',
                  fontWeight: 'bold',
                }}
              >
                <span
                  dangerouslySetInnerHTML={{
                    __html: result._formatted.parent_title,
                  }}
                />
              </a>
              <p
                style={{
                  color: '#ffffff',
                  fontSize: '14px',
                  wordWrap: 'break-word',
                  overflowWrap: 'break-word',
                }}
              >
                <span
                  dangerouslySetInnerHTML={{
                    __html: result._formatted.parent_summary,
                  }}
                />
              </p>
              <div
                style={{
                  marginTop: '10px',
                  display: 'flex',
                  flexWrap: 'wrap',
                  gap: '5px',
                }}
              >
                {result._formatted.parent_keywords.slice(0, 5).map((keyword, i) => (
                  <span
                    key={i}
                    style={{
                      backgroundColor: '#3f2b96',
                      color: '#ffffff',
                      padding: '5px 10px',
                      borderRadius: '15px',
                      fontSize: '12px',
                    }}
                  >
                    <span dangerouslySetInnerHTML={{ __html: keyword }} />
                  </span>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default SearchComponent;
