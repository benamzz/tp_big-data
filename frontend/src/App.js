import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';

// Importation des composants
import Header from './components/Header';
import ObjectList from './components/ObjectList';
import AlertList from './components/AlertList';
import SpaceCanvas from './components/SpaceCanvas';
import ErrorNotification from './components/ErrorNotification';

function App() {
  const [objects, setObjects] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showError, setShowError] = useState(false);

  useEffect(() => {
    // Afficher la notification d'erreur lorsque error change et n'est pas null
    if (error) {
      setShowError(true);
    }
  }, [error]);

  const dismissError = () => {
    setShowError(false);
  };

  useEffect(() => {
    const fetchData = async () => {
      try {
        setIsLoading(true);
        
        // Uniquement effacer l'erreur si la requête précédente a échoué
        if (error) setError(null);

        // Tentative de récupération des données
        const objectsRes = await axios.get('http://localhost:5000/api/space-objects');
        setObjects(objectsRes.data);

        const alertsRes = await axios.get('http://localhost:5000/alerts');
        setAlerts(alertsRes.data);

        setIsLoading(false);
      } catch (error) {
        console.error('Error fetching data:', error);
        setIsLoading(false);
        
        // Gestion des différents types d'erreurs
        if (error.response) {
          // La requête a été faite et le serveur a répondu avec un code d'erreur
          const errorMessage = error.response.data && error.response.data.error 
            ? error.response.data.error 
            : `Erreur serveur: ${error.response.status}`;
          setError(errorMessage);
        } else if (error.request) {
          // La requête a été faite mais aucune réponse n'a été reçue
          setError("Impossible de communiquer avec le serveur. Vérifiez que l'API est en cours d'exécution.");
        } else {
          // Une erreur s'est produite lors de la configuration de la requête
          setError(`Erreur: ${error.message}`);
        }
      }
    };

    fetchData();
    const interval = setInterval(fetchData, 5000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="App">
      <Header />
      
      {showError && (
        <ErrorNotification 
          message={error} 
          onDismiss={dismissError} 
        />
      )}
      
      <div className="main-content">
        <div className="sidebar">
          <ObjectList 
            objects={objects} 
            isLoading={isLoading} 
            error={error} 
          />
          
          <AlertList 
            alerts={alerts} 
            isLoading={isLoading} 
            error={error} 
          />
        </div>
        
        <div className="canvas-container">
          <SpaceCanvas 
            objects={objects} 
            isLoading={isLoading} 
            error={error} 
          />
        </div>
      </div>
    </div>
  );
}

export default App; 