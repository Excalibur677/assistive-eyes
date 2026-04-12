import cv2
import numpy as np
import easyocr
from fuzzywuzzy import fuzz, process
from .models import Medicine


reader = easyocr.Reader(['en'], gpu=False)



def preprocess_image(image):
    """
    Cleans the raw camera image.
    Handles glare, noise, and contrast issues.
    """

   
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

   
    gray = cv2.resize(gray, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)

    
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    threshold = cv2.adaptiveThreshold(
        blurred,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        11,
        2
    )

   
    kernel = np.ones((1, 1), np.uint8)
    cleaned = cv2.morphologyEx(threshold, cv2.MORPH_CLOSE, kernel)

    return cleaned



def crop_medicine_box(image):
    """
    Tries to detect the edges of the medicine box
    and crop out the background clutter.
    """
    try:
        # Find edges
        edges = cv2.Canny(image, 50, 150)

        # Find contours (outlines)
        contours, _ = cv2.findContours(
            edges,
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE
        )

        if not contours:
            return image  # Return original if no box found

        # Find the largest contour (most likely the medicine box)
        largest = max(contours, key=cv2.contourArea)
        x, y, w, h = cv2.boundingRect(largest)

        # Only crop if the detected box is big enough
        if w > 100 and h > 100:
            cropped = image[y:y+h, x:x+w]
            return cropped

        return image  # Return original if box too small

    except:
        return image  # If anything fails, return original



def extract_text_from_image(image):
    results = reader.readtext(image)
    text = ' '.join([res[1] for res in results])
    print("=== RAW OCR TEXT ===")
    print(text)
    print("====================")
    return text


def fuzzy_match_medicine(text):

    words      = text.split()
    candidates = []

    for i in range(len(words)):
        for j in range(i+1, min(i+5, len(words)+1)):
            candidates.append(' '.join(words[i:j]))

    candidates.append(text)

    medicines  = Medicine.objects.all()
    best_match = None
    best_score = 0

    for medicine in medicines:
        for candidate in candidates:

            score1 = fuzz.token_sort_ratio(
                candidate.lower(),
                medicine.name.lower()
            )

            score2 = fuzz.token_sort_ratio(
                candidate.lower(),
                medicine.generic_name.lower()
            ) if medicine.generic_name else 0

            score = max(score1, score2)

            if score > best_score:
                best_score = score
                best_match = medicine.name

    print("=== BEST MATCH ===")
    print("Match:", best_match)
    print("Score:", best_score)
    print("==================")

    if best_score >= 75:
        return best_match

    return None 
def extract_medicine_name(image):

    # Try 1 — read directly without any preprocessing
    text = extract_text_from_image(image)
    print("Try 1 raw text:", text)

    if text.strip():
        result = fuzzy_match_medicine(text)
        if result:
            return result

    # Try 2 — greyscale only
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    text = extract_text_from_image(gray)
    print("Try 2 greyscale text:", text)

    if text.strip():
        result = fuzzy_match_medicine(text)
        if result:
            return result

    # Try 3 — full preprocessing pipeline
    preprocessed = preprocess_image(image)
    cropped      = crop_medicine_box(preprocessed)
    text         = extract_text_from_image(cropped)
    print("Try 3 preprocessed text:", text)

    if text.strip():
        return fuzzy_match_medicine(text)

    return None