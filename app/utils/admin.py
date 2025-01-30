from app.models import Users

def createAdmin():
    if not Users.objects.filter(username="admin").exists():
        Users.objects.create_superuser("admin", "admin@gmail.com", "admin")
        print("Superuser created successfull")
    else:
        print("superuser already exists")