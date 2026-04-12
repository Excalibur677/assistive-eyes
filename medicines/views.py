import json
import base64
import numpy as np
import cv2
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from .models import Medicine
from .ocr_engine import extract_medicine_name
from django.shortcuts import render
from .models import Medicine, ScanHistory

# ── Page Views ──
def standard_view(request):
    return render(request, 'medicines/standard.html')

def accessibility_view(request):
    return render(request, 'medicines/accessibility.html')


# ── API Views ──
@csrf_exempt
def scan_medicine(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            image_data = data.get('image', '')

            if ',' in image_data:
                image_data = image_data.split(',')[1]

            image_bytes = base64.b64decode(image_data)
            np_array = np.frombuffer(image_bytes, np.uint8)
            image = cv2.imdecode(np_array, cv2.IMREAD_COLOR)

            medicine_name = extract_medicine_name(image)
            medicine_name = extract_medicine_name(image)
            print("=== OCR DEBUG ===")
            print("OCR Result:", medicine_name)
            print("=================")
            if not medicine_name:
                return JsonResponse({
                    'success': False,
                    'message': 'No medicine detected. Please try again.'
                })

            medicine = Medicine.objects.filter(
                name__icontains=medicine_name
            ).first()

            if not medicine:
                return JsonResponse({
                    'success': False,
                    'message': f'Medicine "{medicine_name}" not found in database.'
                })

            return JsonResponse({
                'success': True,
                'medicine': {
                    'name': medicine.name,
                    'generic_name': medicine.generic_name,
                    'category': medicine.category,
                    'uses': medicine.uses,
                    'dosage': medicine.dosage,
                    'side_effects': medicine.side_effects,
                    'warnings': medicine.warnings,
                }
            })

        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})

    return JsonResponse({'error': 'Only POST requests allowed'}, status=405)


def get_all_medicines(request):
    medicines = Medicine.objects.all().values(
        'id','name', 'generic_name', 'category', 'uses', 'dosage', 'side_effects','warnings'
    )
    return JsonResponse({'medicines': list(medicines)})

def standard_view(request):
    return render(request, 'medicines/standard.html')


def accessibility_view(request):
    return render(request, 'medicines/accessibility.html')


def admin_dashboard(request):
    return render(request, 'medicines/admin_dashboard.html')

@csrf_exempt
def add_medicine(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        med = Medicine.objects.create(
            name=data['name'],
            generic_name=data.get('generic_name', ''),
            category=data['category'],
            dosage=data['dosage'],
            uses=data['uses'],
            side_effects=data['side_effects'],
            warnings=data.get('warnings', '')
        )
        return JsonResponse({'success': True, 'id': med.id})
    return JsonResponse({'success': False})

@csrf_exempt
def edit_medicine(request, id):
    if request.method == 'POST':
        data = json.loads(request.body)
        Medicine.objects.filter(id=id).update(
            name=data['name'],
            generic_name=data.get('generic_name', ''),
            category=data['category'],
            dosage=data['dosage'],
            uses=data['uses'],
            side_effects=data['side_effects'],
            warnings=data.get('warnings', '')
        )
        return JsonResponse({'success': True})
    return JsonResponse({'success': False})

@csrf_exempt
def delete_medicine(request, id):
    if request.method == 'POST':
        Medicine.objects.filter(id=id).delete()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False})

def admin_login(request):
    return render(request, 'medicines/login.html')


@csrf_exempt
def save_scan_history(request):

    if request.method == 'POST':

        data = json.loads(request.body)

        ScanHistory.objects.create(
            medicine_name = data.get('medicine_name', ''),
            generic_name  = data.get('generic_name', ''),
            category      = data.get('category', ''),
            success       = data.get('success', False),
            message       = data.get('message', '')
        )

        return JsonResponse({'saved': True})

    return JsonResponse({'saved': False})


def get_scan_history(request):

    history = ScanHistory.objects.all().order_by('-scanned_at').values(
        'id',
        'medicine_name',
        'generic_name',
        'category',
        'success',
        'message',
        'scanned_at'
    )

    return JsonResponse({'history': list(history)})