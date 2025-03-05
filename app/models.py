from email.policy import default
from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser
from uuid import uuid4
import os
from datetime import datetime

# Create your models here.

class UsersManager(BaseUserManager):
    def create_user(self, username, email, password, **extra_fields):
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("is_staff", True)
        if not username:
            raise ValueError("username is required")
        if not email:
            raise ValueError("email field is required")
        email = self.normalize_email(email)
        user = self.model(username=username, password=password, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, username, email, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        if not extra_fields.get('is_staff'):
            raise ValueError("Super user must have is_staff=True")
        if not extra_fields.get('is_superuser'):
            raise ValueError('Super user must have is_superuser=True')
        return self.create_user(username, email, password, **extra_fields)

class Users(AbstractBaseUser):
    id = models.UUIDField(default=uuid4, primary_key=True, editable=False)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    username = models.CharField(max_length=255, unique=True)
    email = models.EmailField(max_length=255, unique=True)
    phone = models.CharField(max_length=15, unique=True)
    id_no = models.CharField(max_length=10, unique=True)
    gender = models.CharField(max_length=20)
    password = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_staff = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email','gender','phone']

    objects = UsersManager()

    class Meta:
        db_table = "user"
        verbose_name = "user"
        verbose_name_plural = "users"
    
    def __str__(self):
        return self.email

    def has_module_perms(self, app_label):
        return True

    def has_perm(self, perm, obj=None):
        return True


class Slots(models.Model):
    id = models.UUIDField(default=uuid4, primary_key=True, editable=False)
    slot_id = models.CharField(max_length=50, unique=True)
    floor = models.CharField(max_length=50)
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "slot"
        verbose_name = "slot"
        verbose_name_plural = "slots"

class Parking(models.Model):
    id = models.UUIDField(default=uuid4, primary_key=True, editable=False)
    slot = models.ForeignKey(Slots, on_delete=models.CASCADE)
    vehicle = models.CharField(max_length=10)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "parking"
        verbose_name = "parking"
        verbose_name_plural = "parkings"