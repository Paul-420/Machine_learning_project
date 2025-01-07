import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
import torch
from backend.app import model, class_names

def test_model_prediction():
    dummy_input = torch.randn(1, 3, 224, 224)
    output = model(dummy_input)
    _, predicted_class = torch.max(output, 1)
    assert 0 <= predicted_class.item() < len(class_names)
