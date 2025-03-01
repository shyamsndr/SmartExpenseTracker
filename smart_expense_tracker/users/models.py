from django.db import models
from django.db.models import UniqueConstraint

class User(models.Model):
    u_id = models.AutoField(primary_key=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)
    first_name = models.CharField(max_length=50, blank=True, null=True)
    last_name = models.CharField(max_length=50, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)

    def __str__(self):
        return self.email
    
class SourceOfIncome(models.Model):
    source_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)

    class Meta:
        constraints = [
            UniqueConstraint(fields=['user', 'name'], name='unique_user_source')
        ]

    def __str__(self):
        return self.name