import os
from django.conf import settings
from django.shortcuts import render, redirect
from django.template import loader
from datetime import datetime
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from django.http import HttpResponse, JsonResponse
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from .models import Users, Slots, Parking
from .serializers import UsersSerializers, SlotsSerializers, ParkingSerializers, NewParkingSerializers
from .utils.admin import createAdmin
from django.views.decorators.csrf import csrf_exempt
import json
import cv2
import numpy as np
import base64
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from .services import plate_extraction

CASCADE_PATH = os.path.join(settings.BASE_DIR, 'app/static/plates.xml')
plate_cascade = cv2.CascadeClassifier(CASCADE_PATH)

# Directory to store cropped plate images
PLATES_DIR = os.path.join(settings.MEDIA_ROOT, 'plates')
if not os.path.exists(PLATES_DIR):
    os.makedirs(PLATES_DIR)

# Create your views here.

createAdmin()

@csrf_exempt
def detect_plate(request):
    if request.method == "POST":
        try:
            image = None

            # Handle File Upload (Postman)
            if 'image' in request.FILES:
                uploaded_file = request.FILES['image']
                file_path = default_storage.save(f"temp/{uploaded_file.name}", ContentFile(uploaded_file.read()))
                image_path = os.path.join(settings.MEDIA_ROOT, file_path)
                image = cv2.imread(image_path)

            # Handle Base64 Image (From Client)
            elif request.content_type == 'application/json':
                data = json.loads(request.body)
                image_data = data.get("image")  # Base64 encoded image
                
                if image_data:
                    image_data = image_data.split(",")[1]  # Remove Base64 header
                    image_bytes = base64.b64decode(image_data)
                    np_arr = np.frombuffer(image_bytes, np.uint8)
                    image = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

            if image is None:
                return JsonResponse({"error": "No image data received"}, status=400)

            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            plates = plate_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(50, 50))

            if len(plates) == 0:
                return JsonResponse({"message": "No plates detected"}, status=200)

            detected_plates = []

            for i, (x, y, w, h) in enumerate(plates):
                # Crop the plate region
                plate_img = image[y:y+h, x:x+w]

                # Generate a unique filename and save the cropped file
                timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
                filename = f"plate_{timestamp}_{i}.jpg"
                file_path = os.path.join(PLATES_DIR, filename)
                plate_img = cv2.resize(plate_img, (660, 220), interpolation=cv2.INTER_AREA)
                cv2.imwrite(file_path, plate_img)
                number_plates = plate_extraction(plate_img)
                if number_plates == "":
                    pass
                detected_plates.append({
                    "file_path": f"{settings.MEDIA_URL}plates/{filename}",
                    "number_plates": number_plates
                })

            return JsonResponse({"message": "Plates detected", "plates": detected_plates}, status=200)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request method"}, status=405)
    
@api_view(["GET"])
def logOut(req):
    logout(req)
    return redirect("/")

@api_view(["GET", "POST"])
def signin(req):
    if req.method == "GET":
        template = loader.get_template("signin.html")
        context = {}
        return HttpResponse(template.render(context, req))
    
    elif req.method == "POST":
        user = req.data
        try:
            usr = get_object_or_404(Users, username=user['username'])
        except:
            return Response({"message": "Username does not exist", "success": False, "status": status.HTTP_400_BAD_REQUEST})
        if not usr.is_active:
            return Response({"message": "Account does not exist", "success": False, "status": status.HTTP_400_BAD_REQUEST})
        found_user = authenticate(username=user['username'], password=user['password'])
        if not found_user:
            return Response({"message": "The password is incorect", "success": False, "status": status.HTTP_400_BAD_REQUEST})

        token, _ = Token.objects.get_or_create(user=usr)
        token.created = datetime.now()
        token.save()
        login(req, found_user)
        req.session['sessionId'] = str(found_user.id)
        req.session.set_expiry(3600)
        serializer = UsersSerializers(instance=usr)
        return Response({"message": "Successfully loged into your account", "user":serializer.data, "success": True, "token": token.key, "status": status.HTTP_200_OK})

def updateParkingSlot(id):
    slot = Slots.objects.get(id=id)
    if slot.isAvailable:
        slot.isAvailable = False
    else:
        slot.isAvailable = True
    slot.save()

@api_view(["GET", "POST"])
@login_required
def parking(req):
    if req.method == "GET":
        template = loader.get_template("parking.html")
        context = {}
        obj = Parking.objects.all()
        serializer = ParkingSerializers(obj, many=True)
        context["parking"] = serializer.data
        return HttpResponse(template.render(context, req))   

    elif req.method == "POST":
        serializer = NewParkingSerializers(data=req.data)
        if serializer.is_valid():
            serializer.save()
            updateParkingSlot(req.data["slot"])
            return redirect("/")
        return JsonResponse({"message":"An error occured", "success":False})

@csrf_exempt
@api_view(["PUT", "DELETE", "GET"])
@login_required
def user(req, userId):
    obj = Users.objects.get(id=userId)
    if req.method == "DELETE":
        try:
            obj.delete()
        except Exception as e:
            return JsonResponse({"message": str(e), "success":False})
        return JsonResponse({"message":"Successfully deleted user", "success":True})

    elif req.method == "GET":
        serializer = UsersSerializers(instance=obj)            
        return JsonResponse({"data":serializer.data, "success":True})

    elif req.method == "PUT":
        serializer = UsersSerializers(obj, data=req.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse({"message":"Successfully updated user data", "success":True})
        return JsonResponse({"message":"An error has occured try again later!!!", "success":False})

@csrf_exempt
@api_view(["GET", "POST"])
@login_required
def users(req):
    template = loader.get_template("users.html")
    context = {}
    if req.method == "GET":
        obj = Users.objects.all()
        serializer = UsersSerializers(obj, many=True)
        context["users"] = serializer.data
        return HttpResponse(template.render(context, req))

    elif req.method == "POST":
        serializer = UsersSerializers(data=req.data)
        if serializer.is_valid():
            serializer.save()
            # return JsonResponse({"message":"successfully added a new system user", "success":True})
            return redirect("/users")
        return JsonResponse({"message":"An error has occured", "success":False})

@csrf_exempt
@api_view(["PUT", "DELETE", "GET"])
@login_required
def slot(req, id):
    obj = Slots.objects.get(id=id)
    if req.method == "DELETE":
        try:
            obj.delete()
        except Exception as e:
            return JsonResponse({"message": str(e), "success":False})
        return JsonResponse({"message":"Successfully deleted Parking Slot", "success":True})

    elif req.method == "GET":
        serializer = SlotsSerializers(instance=obj)            
        return JsonResponse({"data":serializer.data, "success":True})

    elif req.method == "PUT":
        serializer = SlotsSerializers(obj, data=req.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            print("helo")
            return JsonResponse({"message":"Successfully updated slot's data", "success":True})
        return JsonResponse({"message":"An error has occured try again later!!!", "success":False})

@api_view(["GET", "POST"])
@login_required
def slots(req):
    if req.method == "GET":
        context = {}
        template = loader.get_template("slots.html")
        obj = Slots.objects.all()
        serializer = SlotsSerializers(obj, many=True)
        context["slots"] = serializer.data
        return HttpResponse(template.render(context, req))

    elif req.method == "POST":
        serializer = SlotsSerializers(data=req.data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse({"message":"successfully added a new parking slot", "success":True})
        return JsonResponse({"message":"An error has occured", "success":False})


@api_view(["GET"])
@login_required
def index(req):
    template = loader.get_template("index.html")
    context = {}
    context['isAdmin'] = req.user.is_superuser
    obj = Slots.objects.all()
    serializer = SlotsSerializers(obj, many=True)
    context["slots"] = serializer.data
    return HttpResponse(template.render(context, req))
