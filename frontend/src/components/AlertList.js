import React from 'react';
import './AlertList.css';

const AlertList = ({ alerts, isLoading, error }) => {
  if (isLoading) {
    return (
      <div className="alert-list">
        <h2>Alertes</h2>
        <div className="loading">Chargement des alertes...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="alert-list">
        <h2>Alertes</h2>
        <div className="error-message">
          <p>Impossible de charger les alertes</p>
          <p className="error-details">{error}</p>
        </div>
      </div>
    );
  }

  if (alerts.length === 0) {
    return (
      <div className="alert-list">
        <h2>Alertes</h2>
        <p className="no-alerts">Aucun objet dangereux détecté.</p>
      </div>
    );
  }

  return (
    <div className="alert-list">
      <h2>Alertes</h2>
      <div className="alert-count">
        <span className="count">{alerts.length}</span> objets dangereux détectés
      </div>
      <ul>
        {alerts.map(alert => (
          <li key={alert.id} className="alert-item">
            <div className="alert-header">
              <span className="alert-id">{alert.id}</span>
              <span className="danger-level">DANGER</span>
            </div>
            <div className="alert-type">
              {alert.type}
            </div>
            <div className="alert-details">
              <div className="detail">
                <span className="label">Vitesse:</span>
                <span className="value danger">{alert.vitesse.toFixed(2)} km/s</span>
              </div>
              <div className="detail">
                <span className="label">Taille:</span>
                <span className="value danger">{alert.taille.toFixed(2)} m</span>
              </div>
              <div className="detail">
                <span className="label">Position:</span>
                <span className="value">
                  x: {alert.position.x.toFixed(1)}, 
                  y: {alert.position.y.toFixed(1)}, 
                  z: {alert.position.z.toFixed(1)}
                </span>
              </div>
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
};

export default AlertList; 