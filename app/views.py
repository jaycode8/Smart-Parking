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

# Create your views here.

createAdmin()

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
        print(usr.password)
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
            return HttpResponse({"message":"successfully added a new system user", "success":True})
        return HttpResponse({"message":"An error occured", "success":False})

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
            return JsonResponse({"message":"successfully added a new system user", "success":True})
        return JsonResponse({"message":"An error has occured", "success":False})

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
