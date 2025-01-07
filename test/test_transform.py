import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from PIL import Image
import torch
from backend.app import transform

def test_transform():
    image = Image.new("RGB", (300, 300))
    tensor = transform(image).unsqueeze(0)
    assert tensor.shape == torch.Size([1, 3, 224, 224])
