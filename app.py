from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from torchvision import models, transforms
from PIL import Image
import torch
from torch import nn
import io

# Initialiser l'application FastAPI
app = FastAPI()

# Ajouter la configuration CORS pour permettre les requêtes de React (localhost:3000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend React
    allow_credentials=True,
    allow_methods=["*"],  # Autoriser toutes les méthodes HTTP (GET, POST, etc.)
    allow_headers=["*"],  # Autoriser tous les headers
)

# Charger le modèle avec la même architecture
num_classes = 10  # Remplacez par le nombre réel de classes
model = models.resnet18(pretrained=False)
model.fc = nn.Linear(model.fc.in_features, num_classes)

# Charger les poids sauvegardés
model.load_state_dict(torch.load("bird_classifier_test.pth", map_location=torch.device('cpu')), strict=False)

model.eval()  # Mode évaluation

# Transformations pour l'image
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])

# Route pour tester le service
@app.get("/")
def read_root():
    return {"message": "Bienvenue dans l'API de classification des oiseaux"}

# Route pour prédire une image
@app.post("/predict/")
async def predict(file: UploadFile = File(...)):
    try:
        # Charger l'image depuis le fichier uploadé
        image = Image.open(io.BytesIO(await file.read()))
        image = image.convert("RGB")  # S'assurer que l'image est au format RGB
        
        # Prétraiter l'image
        input_tensor = transform(image).unsqueeze(0)  # Ajouter une dimension batch
        
        # Faire la prédiction
        with torch.no_grad():
            outputs = model(input_tensor)
            _, predicted_class = torch.max(outputs, 1)
        
        # Renvoyer la classe prédite sous le nom 'prediction'
        return {"prediction": predicted_class.item()}  # Utilisation de 'prediction' comme clé
    
    except Exception as e:
        return {"error": str(e)}

