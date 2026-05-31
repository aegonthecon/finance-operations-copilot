#!/usr/bin/env python3
import os, json

# Ensure project root is in PYTHONPATH
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
import sys
sys.path.append(project_root)

from app.utils.gemini_vision import extract_invoice

# Path to sample invoice image (artifact)
sample_path = os.path.abspath(os.path.join(project_root, '..', 'sample_invoice_a_1780242496801.png'))

print('Sample invoice path:', sample_path)

try:
    result = extract_invoice(sample_path)
    print('OCR result:', json.dumps(result, indent=2))
except Exception as e:
    print('Error during OCR:', e)
