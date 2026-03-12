const video    = document.getElementById('webcam');
const statusEl = document.getElementById('status');
const canvas   = document.getElementById('shutter');
const ctx      = canvas.getContext('2d');

let isScanning    = false;
let autoScanLoop  = null;
let foundMedicine = false;

async function startViewfinder() {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({
            video: {
                facingMode: 'environment',
                width:  { ideal: 1920 },
                height: { ideal: 1080 }
            }
        });
        video.srcObject = stream;
        statusEl.innerText = 'System Ready';
        speak('System ready. Press spacebar to start scanning. I will keep trying until I find your medicine.');
    } catch (err) {
        statusEl.innerText = 'Camera Error. Please allow access and refresh.';
        speak('Camera error. Please allow camera access and refresh the page.');
    }
}

document.addEventListener('keydown', (e) => {
    if (e.code === 'Space') {
        e.preventDefault();
        if (!isScanning) {
            startAutoScan();
        }
    }
    if (e.key.toLowerCase() === 'r') {
        speak(statusEl.innerText);
    }
    if (e.key === 'Escape') {
        stopAutoScan();
        statusEl.innerText = 'Scan stopped. Press SPACE to try again.';
        speak('Scan stopped. Press spacebar to try again.');
    }
});

const DATABASE = [
    {
        name: 'Enzoflam SP',
        keys: ['enzoflam', 'enzof', 'enzo', 'aceclofenac', 'aceclo', 'aceclof',
               'acec', 'acelof', 'viralfever', 'viral', 'alkem', 'enzofl', 'nzoflam', 'zoflam'],
        msg: 'Medicine detected: Enzoflam SP. Contains Aceclofenac and Paracetamol. Used for viral fever, pain relief, and inflammation. Do not take on an empty stomach.'
    },
    {
        name: 'Dolo 650 / Paracetamol',
        keys: ['dolo', 'd0lo', 'd010', '650', 'paracetamol', 'paracetam',
               'para', 'ceta', 'amol', 'calpol', 'calp', 'crocin', 'croc', 'p650'],
        msg: 'Medicine detected: Dolo 650 or Paracetamol. Used for fever and pain relief. Usual dose is one tablet every six hours.'
    },
    {
        name: 'Luliconazole',
        keys: ['luliconazole', 'lulifin', 'lulican', 'luli', 'conazole', 'cona', 'luliz'],
        msg: 'Medicine detected: Luliconazole. Antifungal cream for ringworm and fungal skin infections. Apply once daily to the affected area.'
    },
    {
        name: 'Sinarest',
        keys: ['sinarest', 'sinares', 'sinar', 'sina'],
        msg: 'Medicine detected: Sinarest. Used for common cold, blocked nose, runny nose, and sneezing.'
    },
    {
        name: 'Ondem',
        keys: ['ondem', 'ondansetron', 'ondanse', 'vomikind', 'vomik'],
        msg: 'Medicine detected: Ondem. Used to prevent nausea and vomiting.'
    },
    {
        name: 'Combiflam',
        keys: ['combiflam', 'combif', 'combi', 'ibuprofen', 'ibupro', 'brufen', 'flexon'],
        msg: 'Medicine detected: Combiflam. Contains Ibuprofen and Paracetamol. Used for muscle pain and inflammation. Do not take on an empty stomach.'
    },
    {
        name: 'ReNerve',
        keys: ['renerve', 'renerv', 'methylcobalamin', 'methylcob', 'methyl',
               'neurobion', 'neuro', 'mecobal', 'mecob'],
        msg: 'Medicine detected: Re Nerve. A vitamin B12 supplement for nerve damage, numbness, and tingling.'
    },
    {
        name: 'Cilnidipine',
        keys: ['cilnidipine', 'cilacar', 'cilnid', 'cilny', 'ciln'],
        msg: 'Medicine detected: Cilnidipine. A blood pressure medicine for hypertension. Do not skip doses.'
    },
    {
        name: 'Azithromycin',
        keys: ['azithromycin', 'azithral', 'azithro', 'azith', 'azee'],
        msg: 'Medicine detected: Azithromycin. An antibiotic for bacterial infections. Complete the full prescribed course.'
    },
    {
        name: 'Amoxicillin',
        keys: ['amoxicillin', 'amoxicil', 'amoxil', 'mox500', 'amox'],
        msg: 'Medicine detected: Amoxicillin. An antibiotic. Take the full course as prescribed.'
    },
    {
        name: 'Pan 40 / Pantoprazole',
        keys: ['pantoprazole', 'pantop', 'pan40', 'pantin', 'pantocid'],
        msg: 'Medicine detected: Pan 40 or Pantoprazole. Used for acidity and acid reflux. Best taken 30 minutes before meals.'
    },
    {
        name: 'Digene',
        keys: ['digene', 'digen', 'gelusil', 'gelusi', 'antacid'],
        msg: 'Medicine detected: Digene. An antacid for heartburn, gas, and acidity.'
    },
    {
        name: 'Cetirizine',
        keys: ['cetirizine', 'cetiri', 'okacet', 'okace', 'allegra', 'levocet'],
        msg: 'Medicine detected: Cetirizine or Okacet. Antihistamine for allergy and sneezing. May cause drowsiness.'
    },
    {
        name: 'Metformin',
        keys: ['metformin', 'glycomet', 'glycom', 'metfor'],
        msg: 'Medicine detected: Metformin or Glycomet. Controls blood sugar in Type 2 diabetes. Take with meals.'
    },
    {
        name: 'Aspirin / Ecosprin',
        keys: ['ecosprin', 'aspirin', 'aspin', 'disprin'],
        msg: 'Medicine detected: Ecosprin or Aspirin. Used for heart health and blood clot prevention. Take with food.'
    },
    {
        name: 'Becosules / Vitamins',
        keys: ['becosules', 'becosule', 'becos', 'zincovit', 'limcee', 'supradyn', 'revital'],
        msg: 'Medicine detected: Becosules or Multivitamin. For energy and immunity. Take once daily after meals.'
    }
];

const FILTERS = [
    'none',
    'grayscale(100%) contrast(150%) brightness(100%)',
    'grayscale(100%) contrast(400%) brightness(40%)',
    'grayscale(100%) contrast(300%) brightness(60%) invert(100%)',
    'grayscale(100%) contrast(300%) brightness(130%)',
];

function startAutoScan() {
    foundMedicine = false;
    isScanning    = true;
    statusEl.innerText = 'Scanning... Move the medicine slowly in front of the camera.';
    speak('Scanning started. Slowly move the medicine in front of the camera. I will detect it automatically.');

    runOneScan();
    autoScanLoop = setInterval(() => {
        if (!foundMedicine) {
            runOneScan();
        }
    }, 3000);
}

function stopAutoScan() {
    if (autoScanLoop) {
        clearInterval(autoScanLoop);
        autoScanLoop = null;
    }
    isScanning    = false;
    foundMedicine = false;
}

async function runOneScan() {
    if (foundMedicine) return;

    canvas.width  = video.videoWidth  || 1280;
    canvas.height = video.videoHeight || 720;

    let combinedText = '';

    for (let i = 0; i < FILTERS.length; i++) {
        if (foundMedicine) return;

        try {
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            ctx.filter = FILTERS[i];
            ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
            ctx.filter = 'none';

            const result  = await Tesseract.recognize(canvas.toDataURL('image/jpeg', 1.0), 'eng');
            const rawText = result.data.text.toLowerCase();
            const clean   = rawText.replace(/[^a-z0-9]/g, '');

            combinedText += ' ' + rawText + ' ' + clean;

            const match = findBestMatch(combinedText);
            if (match) {
                foundMedicine = true;
                stopAutoScan();
                statusEl.innerText = match.msg;
                speak(match.msg);
                if (navigator.vibrate) navigator.vibrate([200, 100, 200]);
                return;
            }

        } catch (err) {
            console.error(err);
        }
    }

    if (!foundMedicine) {
        statusEl.innerText = 'Still looking... Keep moving the medicine slowly.';
    }
}

function findBestMatch(text) {
    let bestMatch = null;
    let bestScore = 0;

    for (const med of DATABASE) {
        let score = 0;
        for (const key of med.keys) {
            if (text.includes(key)) score++;
        }
        if (score >= 1 && score > bestScore) {
            bestScore = score;
            bestMatch = med;
        }
    }
    return bestMatch;
}

function speak(text) {
    window.speechSynthesis.cancel();
    const s = new SpeechSynthesisUtterance(text);
    s.lang  = 'en-IN';
    s.rate  = 0.88;
    s.pitch = 1;
    window.speechSynthesis.speak(s);
}

startViewfinder();