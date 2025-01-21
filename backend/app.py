from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from torchvision import models, transforms
from PIL import Image
import torch
from torch import nn
import io
from sqlalchemy.orm import Session
from fastapi.responses import JSONResponse
from backend.db_setup import SessionLocal, BirdImage
import base64
# Dictionnaire des classes avec les noms des oiseaux
class_names = [
    "001.Black_footed_Albatross","002.Laysan_Albatross","004.Groove_billed_Ani","010.Red_winged_Blackbird","011.Rusty_Blackbird",
    "013.Bobolink","014.Indigo_Bunting","021.Eastern_Towhee","025.Pelagic_Cormorant","026.Bronzed_Cowbird"
]


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
from fastapi.responses import UJSONResponse
app.default_response_class = UJSONResponse

# Charger le modèle avec la même architecture
num_classes = 10  # Remplacez par le nombre réel de classes
model = models.mobilenet_v2(pretrained=False)
model.classifier[1] = nn.Linear(in_features=model.classifier[1].in_features, out_features=num_classes)
#model.fc = nn.Linear(model.fc.in_features, num_classes)
model.load_state_dict(torch.load("backend/bird_classifier.pth"))

#state_dict = torch.load("backend/bird_classifier.pth", map_location=torch.device('cpu'))
#missing_keys, unexpected_keys = model.load_state_dict(state_dict, strict=False)
#
## Initialiser les poids manquants (si nécessaire)
## Initialiser les poids manquants (si nécessaire)
#for name, param in model.named_parameters():
#    if name in missing_keys:
#        print(f"Initialisation de {name} manuellement.")
#        if param.dim() > 1:  # Si c'est un tenseur avec plus d'une dimension
#            nn.init.xavier_uniform_(param)  # Initialisation Xavier pour les poids
#        else:  # Si c'est un vecteur ou un scalaire
#            nn.init.zeros_(param)  # Initialise à zéro

# Charger les poids sauvegardés
#model.load_state_dict(torch.load("backend/bird_classifier.pth"))

model.eval()  # Mode évaluation

transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])



@app.get("/images/")
def get_images(skip: int = 0, limit: int = 20):
    db: Session = SessionLocal()
    try:
        images = db.query(BirdImage).offset(skip).limit(limit).all()
        image_data = [
            {
                "id": image.id,
                "class_label": image.class_label,
                "image": f"data:image/jpeg;base64,{base64.b64encode(image.image).decode('utf-8')}"
            }
            for image in images
        ]
        return image_data
    finally:
        db.close()



@app.get("/images/{image_id}")
def get_image(image_id: int):
    db: Session = SessionLocal()
    try:
        image = db.query(BirdImage).filter(BirdImage.id == image_id).first()
        if not image:
            return JSONResponse(content={"error": "Image not found"}, status_code=404)
        return JSONResponse(content={"image": f"data:image/jpeg;base64,{image.image.decode('latin1')}"})
    finally:
        db.close()


# Route pour tester le service
@app.get("/")
def read_root():
    return {"message": "Bienvenue dans l'API de classification des oiseaux"}

import threading

# Verrou pour synchroniser l'accès au modèle
model_lock = threading.Lock()

import logging

logging.basicConfig(level=logging.INFO)

# Route pour prédire une image
@app.post("/predict/")
async def predict(file: UploadFile = File(...)):
    try:
        # Charger l'image
        logging.info("Image uploaded successfully.")
        image = Image.open(io.BytesIO(await file.read()))
        image = image.convert("RGB")
        
        # Prétraiter l'image
        input_tensor = transform(image).unsqueeze(0)
        logging.info(f"Input tensor shape: {input_tensor.shape}")
        
        # Prédiction
        #with model_lock:
        #    with torch.no_grad():
        #        outputs = model(input_tensor)
        #        logging.info(f"Model outputs: {outputs}")
        #        _, predicted_class = torch.max(outputs, 1)
        with torch.no_grad():
            outputs = model(input_tensor)
            _, predicted_class = torch.max(outputs, 1)
        
        bird_name = class_names[predicted_class.item()]
        logging.info(f"Predicted bird: {bird_name}")
        
        return {"prediction": bird_name}
    
    except Exception as e:
        logging.error(f"Error during prediction: {str(e)}")
        return {"error": str(e)}
