import React, { useState } from 'react';
import axios from 'axios';

const App = () => {
  const [clientId, setClientId] = useState('');
  const [response, setResponse] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false); // estado de carga

  const handleSearch = async () => {
    setResponse(null);
    setError(null);
    setLoading(true);

    try {
      const res = await axios.post('http://127.0.0.1:5000/consultar_incidencia', {
        "ID Cliente": clientId,
      });
      setResponse(res.data.respuesta);
    } catch (err) {
      setError(err.response?.data?.error || 'Error desconocido');
    } finally {
      setLoading(false); // detener indicador de carga
    }
  };

  return (
    <div className="container">
      <h1>IncidencIA</h1>
      <label htmlFor="client-id">ID Cliente</label>
      <input
        id="client-id"
        type="text"
        value={clientId}
        onChange={(e) => setClientId(e.target.value)}
        placeholder="Introduce el ID del cliente"
      />
      <button onClick={handleSearch} disabled={loading}>
        {loading ? 'Consultando...' : 'Consultar'}
      </button>

      {loading && (
        <div className="spinner">
          <div className="spinner-circle"></div>
          <p>Cargando...</p>
        </div>
      )}

      {response && (
        <div className="result">
          <strong>Respuesta:</strong>
          <p>{response}</p>
        </div>
      )}

      {error && (
        <div className="error">
          <strong>Error:</strong>
          <p>{error}</p>
        </div>
      )}
    </div>
  );
};

export default App;
