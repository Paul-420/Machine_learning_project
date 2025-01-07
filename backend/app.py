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
    "Black_footed_Albatross", "Laysan_Albatross", "Groove_billed_Ani", "Red_winged_Blackbird", "Rusty_Blackbird",
    "Bobolink", "Indigo_Bunting", "Eastern_Towhee", "Pelagic_Cormorant", "Bronzed_Cowbird"
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
model = models.resnet18(pretrained=False)
model.fc = nn.Linear(model.fc.in_features, num_classes)

# Charger les poids sauvegardés
model.load_state_dict(torch.load("backend/bird_classifier.pth", map_location=torch.device('cpu')), strict=False)

model.eval()  # Mode évaluation

# Transformations pour l'image
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
        
        # Obtenir le nom de l'oiseau à partir de la prédiction
        bird_name = class_names[predicted_class.item()]
        
        # Renvoyer le résultat
        return {"prediction": bird_name}
    
    except Exception as e:
        return {"error": str(e)}

