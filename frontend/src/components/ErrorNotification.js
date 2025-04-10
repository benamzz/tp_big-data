import React from 'react';
import './ErrorNotification.css';

const ErrorNotification = ({ message, onDismiss }) => {
  if (!message) return null;

  return (
    <div className="error-notification">
      <div className="error-content">
        <div className="error-icon">
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24">
            <path fill="none" d="M0 0h24v24H0z"/>
            <path fill="currentColor" d="M12 22C6.477 22 2 17.523 2 12S6.477 2 12 2s10 4.477 10 10-4.477 10-10 10zm0-2a8 8 0 1 0 0-16 8 8 0 0 0 0 16zm-1-5h2v2h-2v-2zm0-8h2v6h-2V7z"/>
          </svg>
        </div>
        
        <div className="error-message-container">
          <h3>Erreur</h3>
          <p>{message}</p>
        </div>
        
        <button className="dismiss-button" onClick={onDismiss}>
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24">
            <path fill="none" d="M0 0h24v24H0z"/>
            <path fill="currentColor" d="M12 10.586l4.95-4.95 1.414 1.414-4.95 4.95 4.95 4.95-1.414 1.414-4.95-4.95-4.95 4.95-1.414-1.414 4.95-4.95-4.95-4.95L7.05 5.636z"/>
          </svg>
        </button>
      </div>
    </div>
  );
};

export default ErrorNotification; 