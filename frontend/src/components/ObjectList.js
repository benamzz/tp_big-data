import React from 'react';
import './ObjectList.css';

const ObjectList = ({ objects, isLoading, error }) => {
  if (isLoading) {
    return (
      <div className="object-list">
        <h2>Objets Détectés</h2>
        <div className="loading">Chargement des données...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="object-list">
        <h2>Objets Détectés</h2>
        <div className="error-message">
          <p>Impossible de charger les données</p>
          <p className="error-details">{error}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="object-list">
      <h2>Objets Détectés</h2>
      {objects.length === 0 ? (
        <p className="no-data">Aucun objet détecté pour le moment.</p>
      ) : (
        <ul>
          {objects.map(obj => (
            <li key={obj.id} className="object-item">
              <div className="object-header">
                <span className="object-id">{obj.id}</span>
                <span className={`object-type ${obj.type}`}>{obj.type}</span>
              </div>
              <div className="object-details">
                <div className="detail">
                  <span className="label">Vitesse:</span>
                  <span className="value">{obj.vitesse.toFixed(2)} km/s</span>
                </div>
                <div className="detail">
                  <span className="label">Taille:</span>
                  <span className="value">{obj.taille.toFixed(2)} m</span>
                </div>
                <div className="detail">
                  <span className="label">Position:</span>
                  <span className="value">
                    x: {obj.position.x.toFixed(1)}, 
                    y: {obj.position.y.toFixed(1)}, 
                    z: {obj.position.z.toFixed(1)}
                  </span>
                </div>
              </div>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

export default ObjectList; 