import os
from django.conf import settings
from django.core.paginator import Paginator
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
from django.contrib.auth.hashers import make_password
from .serializers import UsersSerializers, SlotsSerializers, ParkingSerializers, NewParkingSerializers
from .utils.admin import createAdmin
from django.views.decorators.csrf import csrf_exempt
import json
import cv2
import numpy as np
import base64
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from .services import plate_extraction, bright_plate_extraction
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

CASCADE_PATH = os.path.join(settings.BASE_DIR, 'static/plates.xml')
plate_cascade = cv2.CascadeClassifier(CASCADE_PATH)

# Directory to store cropped plate images
PLATES_DIR = os.path.join(settings.MEDIA_ROOT, 'plates')
if not os.path.exists(PLATES_DIR):
    os.makedirs(PLATES_DIR)

# Create your views here.

try:
    createAdmin()
except:
    pass

@csrf_exempt
def detect_plate(request):
    if request.method == "POST":
        try:
            image = None
            channel_layer = get_channel_layer()

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

                if not number_plates:
                    number_plates = bright_plate_extraction(plate_img)

                if number_plates == "":
                    continue

                detected_plates.append({
                    "file_path": f"{settings.MEDIA_URL}plates/{filename}",
                    "number_plates": number_plates
                })
            try:
                exist_parking = Parking.objects.get(vehicle=number_plates)
                update_parking_slot(exist_parking.slot.id)
                exist_parking.delete()
                async_to_sync(channel_layer.group_send)(
                    "notification",
                    {"type":"send_message", "message":"Car Unpacked"}
                )
                return JsonResponse({"message": "Car unparked"}, status=200)

            except Parking.DoesNotExist:
                available_slot = Slots.objects.filter(is_available=True).first()

                if not available_slot:
                    async_to_sync(channel_layer.group_send)(
                        "notification",
                        {"type":"send_message", "message":"No available parking slots at the moment"}
                    )
                    return JsonResponse({"error": "No available parking slots at the moment"}, status=400)

                park_data = {
                    "slot":available_slot.id,
                    "vehicle":number_plates
                }
                serializer = NewParkingSerializers(data=park_data)
                if serializer.is_valid():
                    serializer.save()
                    update_parking_slot(available_slot.id)
                    async_to_sync(channel_layer.group_send)(
                        "notification",
                        {"type":"send_message", "message":f"{number_plates} assigned slot {available_slot.slot_id} located at {available_slot.floor}"}
                    )
                    
                    return JsonResponse({"message": f"{number_plates} assigned slot {available_slot.slot_id} located at {available_slot.floor}"}, status=200)

                async_to_sync(channel_layer.group_send)(
                    "notification",
                    {"type":"send_message", "message":f"Unable to auto park {number_plates} at the moment try manuall assign"}
                )
                return JsonResponse({"message": f"Unable to auto park {number_plates} at the moment try manuall assign"}, status=200)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request method"}, status=405)
    
@api_view(["GET"])
def logOut(req):
    logout(req)
    return redirect("/")

@csrf_exempt
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
            return Response({"message": "Username does not exist", "success": False}, status=404)
        if not usr.is_active:
            return Response({"message": "Account does not exist", "success": False}, status=404)
        found_user = authenticate(username=user['username'], password=user['password'])
        if not found_user:
            return Response({"message": "The password is incorect", "success": False}, status=400)

        login(req, found_user)
        req.session['sessionId'] = str(found_user.id)
        req.session.set_expiry(3600)
        serializer = UsersSerializers(instance=usr)
        return Response({"message": "Successfully loged into your account", "user":serializer.data, "success": True}, status=200)

def update_parking_slot(id):
    slot = Slots.objects.get(id=id)
    if slot.is_available:
        slot.is_available = False
    else:
        slot.is_available = True
    slot.save()

@api_view(["DELETE"])
def parked_car(req, id):
    obj = Parking.objects.get(id=id)
    update_parking_slot(obj.slot.id)
    obj.delete()
    return JsonResponse({"message": "Car unparked"}, status=200)


@api_view(["GET", "POST"])
@login_required
def parking(req):
    if req.method == "GET":
        template = loader.get_template("parking.html")
        page = req.GET.get("page", 1)
        obj = Parking.objects.all().order_by("-created_at")
        paginator = Paginator(obj, 10)
        paginated_data = paginator.get_page(page)
        serializer = ParkingSerializers(paginated_data, many=True)
        context = {
            "parking": serializer.data,
            "page": paginated_data.number,
            "total_pages": paginator.num_pages,
            "isAdmin": req.user.is_superuser
        }
        return HttpResponse(template.render(context, req)) 

    elif req.method == "POST":
        serializer = NewParkingSerializers(data=req.data)
        if serializer.is_valid():
            serializer.save()
            update_parking_slot(req.data["slot"])
            return redirect("/")
        return Response({"message":"An error occured", "success":False}, status=400)

@csrf_exempt
@api_view(["PUT", "DELETE", "GET"])
@login_required
def user(req, userId):
    obj = Users.objects.get(id=userId)
    if req.method == "DELETE":
        try:
            obj.delete()
            return Response({"message":"Successfully deleted user", "success":True}, status=200)
        except Exception as e:
            return Response({"message": str(e), "success":False}, status=400)

    elif req.method == "GET":
        serializer = UsersSerializers(instance=obj)            
        return Response({"data":serializer.data, "success":True}, status=200)

    elif req.method == "PUT":
        req.data["password"] = make_password(req.data["password"])
        serializer = UsersSerializers(obj, data=req.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message":"Successfully updated user data", "success":True}, status=200)
        return Response({"message":"An error has occured try again later!!!", "success":False}, status=400)

@csrf_exempt
@api_view(["GET", "POST"])
@login_required
def users(req):
    template = loader.get_template("users.html")
    if req.method == "GET":
        page = req.GET.get("page", 1)
        obj = Users.objects.all().order_by("-created_at")
        paginator = Paginator(obj, 10)
        paginated_users = paginator.get_page(page)
        serializer = UsersSerializers(paginated_users, many=True)
        context = {
            "users": serializer.data,
            "page": paginated_users.number,
            "total_pages": paginator.num_pages,
            "isAdmin": req.user.is_superuser
        }
        return HttpResponse(template.render(context, req))

    elif req.method == "POST":
        serializer = UsersSerializers(data=req.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message":"successfully added a new system user", "success":True}, status=200)
        return Response({"message":"An error has occured", "success":False}, status=400)

@api_view(["PUT", "DELETE", "GET"])
@login_required
def slot(req, id):
    obj = Slots.objects.get(id=id)
    if req.method == "DELETE":
        try:
            obj.delete()
            return Response({"message":"Successfully deleted Parking Slot", "success":True}, status=200)
        except Exception as e:
            return Response({"message": str(e), "success":False}, status=400)

    elif req.method == "GET":
        serializer = SlotsSerializers(instance=obj)            
        return Response({"data":serializer.data, "success":True}, status=200)

    elif req.method == "PUT":
        serializer = SlotsSerializers(obj, data=req.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message":"Successfully updated slot's data", "success":True}, status=200)
        return Response({"message":"An error has occured try again later!!!", "success":False}, status=400)

@api_view(["GET", "POST"])
@login_required
def slots(req):
    if req.method == "GET":
        template = loader.get_template("slots.html")
        page = req.GET.get("page", 1)
        obj = Slots.objects.all().order_by("-created_at")
        paginator = Paginator(obj, 10)
        paginated_slots = paginator.get_page(page)
        serializer = SlotsSerializers(paginated_slots, many=True)
        context = {
            "slots": serializer.data,
            "page": paginated_slots.number,
            "total_pages": paginator.num_pages,
            "isAdmin": req.user.is_superuser
        }
        return HttpResponse(template.render(context, req))

    elif req.method == "POST":
        serializer = SlotsSerializers(data=req.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message":"successfully added a new parking slot", "success":True}, status=200)

        return Response({"message":"An error has occured", "success":False}, status=400)

@api_view(["GET"])
@login_required
def index(req):
    template = loader.get_template("index.html")
    context = {}
    context['isAdmin'] = req.user.is_superuser
    obj = Slots.objects.filter(is_available=True)
    serializer = SlotsSerializers(obj, many=True)
    context["slots"] = serializer.data
    return HttpResponse(template.render(context, req))
