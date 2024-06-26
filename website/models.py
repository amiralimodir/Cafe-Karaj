from django.db import models

class User(models.Model):
    username = models.CharField(max_length=255, primary_key=True)
    full_name = models.CharField(max_length=255)
    email = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    phone_number = models.IntegerField()

    def __str__(self):
        return self.username
