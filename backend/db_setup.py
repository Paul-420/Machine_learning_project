from sqlalchemy import create_engine, Column, Integer, String, LargeBinary
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite:///./bird_data.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class BirdImage(Base):
    __tablename__ = "bird_images"
    id = Column(Integer, primary_key=True, index=True)
    image = Column(LargeBinary, nullable=False)  # Contenu binaire de l'image
    class_label = Column(String, nullable=False)  # Classe de l'image

Base.metadata.create_all(bind=engine)

import os
from PIL import Image
from sqlalchemy.orm import Session

def load_images_to_db(folder_path, db: Session):
    """
    Charge toutes les images d'un dossier dans la base de données.
    Chaque sous-dossier correspond à une classe.
    """
    for class_name in os.listdir(folder_path):
        class_path = os.path.join(folder_path, class_name)
        if os.path.isdir(class_path):  # Vérifie que c'est un dossier
            for image_name in os.listdir(class_path):
                image_path = os.path.join(class_path, image_name)
                try:
                    with open(image_path, "rb") as img_file:
                        image_data = img_file.read()
                    
                    # Ajouter l'image à la base de données
                    new_image = BirdImage(image=image_data, class_label=class_name)
                    db.add(new_image)
                    db.commit()
                except Exception as e:
                    print(f"Erreur lors du traitement de {image_path}: {e}")

# Exemple d'utilisation
if __name__ == "__main__":
    folder_path = "D:/ML_project/CUB_200_2011/CUB_200_2011/images"
    db = SessionLocal()
    load_images_to_db(folder_path, db)
    db.close()