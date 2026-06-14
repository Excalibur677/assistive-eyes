# 👁️ Assistive Eyes — Medicine Identification System

> A dual-mode medicine label reader built to empower both sighted users and visually impaired individuals through computer vision and voice accessibility.

---

## 🧠 Overview

**Assistive Eyes** is an AI-powered medicine label recognition system that uses **OpenCV + EasyOCR** to extract text from medicine packaging via live webcam, then matches it against a structured medicine database using fuzzy string matching. The system ships with two distinct modes — a standard web dashboard for sighted users and a voice-driven accessibility mode designed specifically for blind users.

---

## ✨ Features

- 📷 **Live Webcam Scanning** — Real-time medicine label detection via browser or server-side camera feed
- 🔍 **OpenCV Preprocessing** — Glare reduction, geometry correction, and image sharpening for improved OCR accuracy
- 🧾 **EasyOCR Text Extraction** — Deep learning-based text recognition (PyTorch + torchvision backend)
- 🔗 **Fuzzy Medicine Matching** — FuzzyWuzzy + python-Levenshtein for tolerant name matching against the medicine database
- 🔊 **Voice Accessibility Mode** — Keyboard-driven (`SPACEBAR` to scan, `R` to repeat, `ESC` to stop) with Web Speech API for text-to-speech output
- 🛠️ **Admin Dashboard** — Django-backed interface for managing the medicine database
- 📦 **Structured Medicine Data** — JSON-based medicine dataset (`medicines_data_fixed.json`) with standardized entries
- 🌐 **REST API** — Django REST Framework endpoints for programmatic access

---

## 🏗️ Architecture

```
assistive-eyes/
│
├── assistive_eyes/         # Django project root (settings, urls, wsgi)
├── medicines/              # Core Django app
│   ├── ocr_engine.py       # OpenCV preprocessing + EasyOCR extraction pipeline
│   ├── models.py           # Medicine database models
│   └── views.py            # API views + webcam scan handler
│
├── acess.html              # Accessibility mode UI (voice-first, keyboard-driven)
├── acesss.js               # Tesseract.js client-side OCR for offline accessibility mode
├── medicines_data.json     # Raw medicine dataset
├── medicines_data_fixed.json  # Cleaned & normalized dataset
├── test_ocr.py             # OCR pipeline integration test
├── test_medicine.jpg       # Sample medicine image for testing
├── manage.py               # Django management entry point
└── requirements.txt        # Python dependencies
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | Django 6.0.4, Django REST Framework 3.17.1, Python 3.13 |
| **Computer Vision** | OpenCV 4.13 (`opencv-python`, `opencv-python-headless`) |
| **OCR** | EasyOCR 1.7.2, Tesseract.js 5 (client-side fallback) |
| **ML Runtime** | PyTorch 2.11.0, TorchVision 0.26.0 |
| **String Matching** | FuzzyWuzzy 0.18.0, python-Levenshtein 0.27.3, RapidFuzz 3.14.5 |
| **Image Processing** | Pillow 12.2.0, scikit-image 0.26.0 |
| **Database** | SQLite (default Django DB) |
| **Frontend** | HTML5, CSS3, JavaScript, Web Speech API |
| **Data Formats** | JSON, Excel (openpyxl), DOCX (python-docx) |

---

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- pip
- Webcam (for live scanning mode)

### Installation

```bash
# Clone the repo
git clone https://github.com/Excalibur677/assistive-eyes.git
cd assistive-eyes

# Create virtual environment
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run Django migrations
python manage.py migrate

# Start the development server
python manage.py runserver
```

### Quick OCR Test

```bash
# Place a medicine image as test_medicine.jpg in the root, then:
python test_ocr.py
```

This runs the full pipeline: image load → OpenCV preprocessing → EasyOCR extraction → fuzzy medicine match → result output.

---

## 🖥️ Usage

### Standard Mode
Navigate to `http://localhost:8000` — use the webcam feed to scan medicine labels. Results are displayed with medicine name, usage, and dosage info from the database.

### Accessibility Mode (Voice-First)
Open `acess.html` directly in a browser or serve it via Django:

| Key | Action |
|-----|--------|
| `SPACEBAR` | Capture frame and start OCR scan |
| `R` | Repeat last spoken result |
| `ESC` | Stop scanning |

Results are read aloud via the Web Speech API — no screen interaction required.

---

## 📊 How It Works

```
Webcam Frame
     │
     ▼
OpenCV Preprocessing
 ├── Glare reduction
 ├── Geometry correction
 └── Sharpening / binarization
     │
     ▼
EasyOCR Text Extraction
 └── Deep learning OCR (PyTorch backend)
     │
     ▼
FuzzyWuzzy Matching
 └── Levenshtein distance against medicines DB
     │
     ▼
Result → Web UI / Voice Output (TTS)
```

---

## 📦 Dependencies (Key)

```
Django==6.0.4
easyocr==1.7.2
opencv-python==4.13.0.92
torch==2.11.0
fuzzywuzzy==0.18.0
python-Levenshtein==0.27.3
djangorestframework==3.17.1
pillow==12.2.0
scikit-image==0.26.0
```

Full list in [`requirements.txt`](./requirements.txt).

---

## 🤝 Contributing

Pull requests are welcome. For major changes, open an issue first to discuss what you'd like to change.

1. Fork the repo
2. Create your branch: `git checkout -b feature/your-feature`
3. Commit changes: `git commit -m 'Add your feature'`
4. Push: `git push origin feature/your-feature`
5. Open a Pull Request

---

## 👨‍💻 Author

**Sumit Kumar**  
B.Tech CSE @ Pimpri Chinchwad University, Pune  
[GitHub](https://github.com/Excalibur677)

---

## 📄 License

This project is open source. Feel free to use and build on it.
