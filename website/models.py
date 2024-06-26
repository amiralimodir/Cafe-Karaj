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
    
    @classmethod
    def count_products_based_on_stock(cls):
        storage = {item.name: item.amount for item in Storage.objects.all()}
        product_counts = {}

        for product in cls.objects.all():
            possible_counts = []
            if product.sugar > 0:
                possible_counts.append(storage.get('sugar', 0) // product.sugar)
            if product.coffee > 0:
                possible_counts.append(storage.get('coffee', 0) // product.coffee)
            if product.flour > 0:
                possible_counts.append(storage.get('flour', 0) // product.flour)
            if product.chocolate > 0:
                possible_counts.append(storage.get('chocolate', 0) // product.chocolate)
            
            if possible_counts:
                product_counts[product.name] = min(possible_counts)
            else:
                product_counts[product.name] = 0

        return product_counts