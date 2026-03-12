import cv2
import django
import os
import sys

# Setup Django
sys.path.append('C:\\Users\\Sumit\\Downloads\\ASSITIVE EYE\\assistive_eyes')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'assistive_eyes.settings')
django.setup()

from medicines.ocr_engine import extract_medicine_name

# Load a test image of a medicine box
image = cv2.imread('test_medicine.jpg')

if image is None:
    print("ERROR: Image not found!")
else:
    result = extract_medicine_name(image)
    print(f"\nFINAL RESULT: {result}")