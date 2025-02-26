from django.db import models

# Create your models here.
class User(models.Model):
    u_id = models.AutoField(primary_key=True)
    email = models.EmailField(unique=True)  # Ensures email is unique
    password = models.CharField(max_length=255)

    def __str__(self):
        return self.email
