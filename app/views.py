from django.shortcuts import render
from django.template import loader
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from django.http import HttpResponse
from .models import Users
from .serializers import UsersSerializers

# Create your views here.

@api_view(["GET"])
def signin(req):
    template = loader.get_template("signin.html")
    context = {}
    return HttpResponse(template.render(context, req))

@api_view(["GET", "POST"])
def users(req):
    template = loader.get_template("users.html")
    context = {}
    if req.method == "GET":
        obj = Users.objects.all()
        serializer = UsersSerializers(obj, many=True)
        context["users"] = serializer.data
    if req.method == "POST":
        serializer = UsersSerializers(data=req.data)
        if serializer.is_valid():
            serializer.save()
            context["message"] = "successfully added a new system user"
            context["color"] = "bg-green-500"
        else:
            context["color"] = "bg-red-500"
            context["message"] = "An error has occured"
    return HttpResponse(template.render(context, req))

@api_view(["GET"])
def slots(req):
    template = loader.get_template("slots.html")
    context = {}
    return HttpResponse(template.render(context, req))

@api_view(["GET"])
def index(req):
    template = loader.get_template("index.html")
    context = {}
    return HttpResponse(template.render(context, req))
