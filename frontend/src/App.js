import React, { useState, useEffect } from "react";
import "./App.css";

function App() {
  const [file, setFile] = useState(null);
  const [prediction, setPrediction] = useState("");
  const [images, setImages] = useState([]);

  // Charger les images depuis le backend
  useEffect(() => {
    fetch("http://localhost:8000/images")
      .then((response) => response.json())
      .then((data) => setImages(data))
      .catch((error) => console.error("Erreur lors du chargement des images :", error));
  }, []);

  // Gestion du fichier sélectionné
  const handleFileChange = (event) => {
    setFile(event.target.files[0]);
  };

  // Envoi du fichier pour la prédiction
  const handleSubmit = async (event) => {
    event.preventDefault();
    if (!file) {
      alert("Veuillez sélectionner une image !");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await fetch("http://localhost:8000/predict/", {
        method: "POST",
        body: formData,
      });
      const data = await response.json();
      if (response.ok) {
        setPrediction(`Prédiction : ${data.prediction}`);
      } else {
        alert(`Erreur : ${data.error}`);
      }
    } catch (error) {
      alert(`Erreur réseau : ${error.message}`);
    }
  };

  return (
    <div className="container">
      <h1>Classification des Oiseaux</h1>

      {/* Formulaire d'upload */}
      <form onSubmit={handleSubmit}>
        <input type="file" onChange={handleFileChange} />
        <button type="submit">Envoyer</button>
      </form>

      {/* Affichage de la prédiction */}
      {prediction && <p className="prediction">{prediction}</p>}

      {/* Affichage des images enregistrées */}
      <div className="saved-images">
        <h2>Images enregistrées</h2>
        <div className="image-grid">
          {images.map((image) => (
            <div className="image-card" key={image.id}>
              {/* Affichage de l'image en base64 */}
              <img src={image.image} alt={image.class_label} />
              <p>{image.class_label}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default App;
