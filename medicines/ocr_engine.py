import cv2
import numpy as np
import easyocr
from fuzzywuzzy import fuzz, process
from .models import Medicine

# Initialize EasyOCR reader once (takes time to load)
reader = easyocr.Reader(['en'], gpu=False)


# ─────────────────────────────────────────
# STEP A: Image Pre-Processing
# ─────────────────────────────────────────
def preprocess_image(image):
    """
    Cleans the raw camera image.
    Handles glare, noise, and contrast issues.
    """

    # 1. Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # 2. Resize for better OCR accuracy
    gray = cv2.resize(gray, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)

    # 3. Apply Gaussian Blur to reduce noise/graininess
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    # 4. Adaptive Thresholding
    # This handles uneven lighting and glare on foil packaging
    threshold = cv2.adaptiveThreshold(
        blurred,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        11,
        2
    )

    # 5. Remove small noise dots
    kernel = np.ones((1, 1), np.uint8)
    cleaned = cv2.morphologyEx(threshold, cv2.MORPH_CLOSE, kernel)

    return cleaned


# ─────────────────────────────────────────
# STEP B: Detect and Crop Medicine Box
# ─────────────────────────────────────────
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


# ─────────────────────────────────────────
# STEP C: Extract Raw Text with EasyOCR
# ─────────────────────────────────────────
def extract_text_from_image(image):
    """
    Runs EasyOCR on the cleaned image.
    Returns all detected text as one string.
    """
    results = reader.readtext(image, detail=0)  # detail=0 = text only
    full_text = ' '.join(results)
    print(f"[OCR RAW TEXT]: {full_text}")  # For debugging
    return full_text


# ─────────────────────────────────────────
# STEP D: Fuzzy Match OCR Text to Database
# ─────────────────────────────────────────
def fuzzy_match_medicine(raw_text):
    """
    Takes raw OCR text and finds the closest
    matching medicine name in the database.
    """

    # Get all medicine names from database
    all_medicines = Medicine.objects.values_list('name', flat=True)
    medicine_names = list(all_medicines)

    if not medicine_names:
        return None

    # Split raw OCR text into individual words
    words = raw_text.split()

    best_match = None
    best_score = 0

    # Try matching each word and combination against database
    for i in range(len(words)):
        for j in range(i+1, min(i+4, len(words)+1)):
            candidate = ' '.join(words[i:j])

            # Fuzzy match this candidate against all medicine names
            match, score = process.extractOne(
                candidate,
                medicine_names,
                scorer=fuzz.token_sort_ratio
            )

            print(f"[FUZZY] '{candidate}' → '{match}' (score: {score})")

            if score > best_score:
                best_score = score
                best_match = match

    # Only accept match if confidence is above 70%
    if best_score >= 70:
        print(f"[MATCH FOUND]: {best_match} with score {best_score}")
        return best_match
    else:
        print(f"[NO MATCH]: Best was {best_match} at {best_score}%")
        return None


# ─────────────────────────────────────────
# MAIN FUNCTION (called by views.py)
# ─────────────────────────────────────────
def extract_medicine_name(image):
    """
    Full pipeline:
    Raw image → Cleaned → Cropped → OCR → Fuzzy Match → Medicine Name
    """
    # Step 1: Preprocess
    cleaned = preprocess_image(image)

    # Step 2: Crop
    cropped = crop_medicine_box(cleaned)

    # Step 3: Extract text
    raw_text = extract_text_from_image(cropped)

    if not raw_text.strip():
        return None

    # Step 4: Fuzzy match
    medicine_name = fuzzy_match_medicine(raw_text)

    return medicine_name