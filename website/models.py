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

class Order(models.Model):
    id = models.AutoField(primary_key=True)
    username = models.ForeignKey(User, on_delete=models.CASCADE)
    products = models.CharField(max_length=255)
    purchase_amount = models.IntegerField()
    type = models.BinaryField()

    def __str__(self):
        return str(self.id)

    @classmethod
    def get_order(cls, order_id):
        try:
            order = cls.objects.get(id=order_id)
            user = order.username
            order_products = OrderProduct.objects.filter(order=order)
            products = [op.product for op in order_products]

            return {
                'order_id': order.id,
                'user': {
                    'username': user.username,
                    'full_name': user.full_name,
                    'email': user.email,
                    'phone_number': user.phone_number
                },
                'products': [{'id': p.id, 'name': p.name, 'price': p.price} for p in products],
                'purchase_amount': order.purchase_amount,
                'type': order.type
            }
        except cls.DoesNotExist:
            return None

class Admin(models.Model):
    username = models.CharField(max_length=255, primary_key=True)
    email = models.CharField(max_length=255)
    password = models.CharField(max_length=255)

    def __str__(self):
        return self.username

class Storage(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    amount = models.IntegerField()

    def __str__(self):
        return self.name