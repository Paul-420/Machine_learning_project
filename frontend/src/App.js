import React, { useState } from 'react';

function App() {
  const [file, setFile] = useState(null);
  const [prediction, setPrediction] = useState("");

  const handleFileChange = (event) => {
    setFile(event.target.files[0]);
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    if (!file) {
      alert("Veuillez sélectionner une image !");
      return;
    }
  
    const formData = new FormData();
    formData.append("file", file);
  
    try {
      const response = await fetch("http://localhost:8000/predict", {
        method: "POST",
        body: formData,
      });
      const data = await response.json();
      if (response.ok) {
        setPrediction(`Prédiction : ${data.prediction}`);  // 'prediction' doit correspondre à ce qui est renvoyé par l'API
      } else {
        alert(`Erreur : ${data.error}`);
      }
    } catch (error) {
      alert(`Erreur réseau : ${error.message}`);
    }
  };
  

  return (
    <div style={{ padding: "20px", textAlign: "center" }}>
      <h1>Classification des Oiseaux</h1>
      <form onSubmit={handleSubmit}>
        <input type="file" onChange={handleFileChange} />
        <button type="submit">Envoyer</button>
      </form>
      {prediction && <p>{prediction}</p>}
    </div>
  );
}

export default App;
