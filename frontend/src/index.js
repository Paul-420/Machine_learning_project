import React from "react";
import ReactDOM from "react-dom/client"; // Important : utiliser 'react-dom/client'
import App from "./App";

// Assurez-vous que l'élément 'root' existe dans votre HTML (index.html)
const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(<App />);
