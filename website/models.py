from django.db import models

class User(models.Model):
    username = models.CharField(max_length=255, primary_key=True)
    full_name = models.CharField(max_length=255)
    email = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    phone_number = models.IntegerField()

    def __str__(self):
        return self.username

class Product(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    sugar = models.IntegerField()
    coffee = models.IntegerField()
    flour = models.IntegerField()
    chocolate = models.IntegerField()
    vertical = models.BinaryField()
    price = models.IntegerField()

    def __str__(self):
        return self.name
    
    @classmethod
    def add_product(cls, name, sugar, coffee, flour, chocolate, vertical, price):
        product = cls(
            name=name,
            sugar=sugar,
            coffee=coffee,
            flour=flour,
            chocolate=chocolate,
            vertical=vertical,
            price=price
        )
        product.save()
        return product