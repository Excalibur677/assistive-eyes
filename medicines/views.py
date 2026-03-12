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
        'name', 'generic_name', 'category', 'uses', 'dosage', 'side_effects'
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