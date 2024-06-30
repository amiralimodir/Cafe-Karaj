from django.db import models, transaction, IntegrityError
from django.db.models import F
import json

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
    order_type = models.BooleanField()

    def __str__(self):
        return str(self.id)

    @classmethod
    @transaction.atomic
    def get_order(cls, username, products, order_type):
        total_price = 0


        for product_id, quantity in products:
            product = Product.objects.get(id=product_id)
            sugar_needed = product.sugar * quantity
            coffee_needed = product.coffee * quantity
            flour_needed = product.flour * quantity
            chocolate_needed = product.chocolate * quantity

            try:
                sugar_stock = Storage.objects.get(name='sugar').amount
                coffee_stock = Storage.objects.get(name='coffee').amount
                flour_stock = Storage.objects.get(name='flour').amount
                chocolate_stock = Storage.objects.get(name='chocolate').amount
            except Storage.DoesNotExist:
                return False, 'One or more components are missing from storage.'

            if sugar_needed > sugar_stock or coffee_needed > coffee_stock or flour_needed > flour_stock or chocolate_needed > chocolate_stock:
                return False, f'Not enough stock for {product.name}.'

            total_price += product.price * quantity

    
        for product_id, quantity in products:
            product = Product.objects.get(id=product_id)
            Storage.objects.filter(name='sugar').update(amount=models.F('amount') - product.sugar * quantity)
            Storage.objects.filter(name='coffee').update(amount=models.F('amount') - product.coffee * quantity)
            Storage.objects.filter(name='flour').update(amount=models.F('amount') - product.flour * quantity)
            Storage.objects.filter(name='chocolate').update(amount=models.F('amount') - product.chocolate * quantity)


        order = cls.objects.create(
            username=username,
            products=json.dumps(products),
            purchase_amount=total_price,
            order_type=order_type
        )

        UserOrder.objects.create(user=User, order=Order)
        for product_id, quantity in products:
            OrderProduct.objects.create(order=order, product_id=product_id, quantity=quantity)
        
        return True, 'Order placed successfully.'

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
    
    @classmethod
    def update_storage(cls, ingredient_name, quantity):
        try:
            storage_item = cls.objects.get(name=ingredient_name)
            storage_item.amount = F('amount') + quantity
            storage_item.save()
            storage_item.refresh_from_db()
            return {
                'status': 'success',
                'name': storage_item.name,
                'amount': storage_item.amount
            }
        except cls.DoesNotExist:
            return {
                'status': 'error',
                'message': f"Ingredient {ingredient_name} does not exist in storage."
            }
    
class UserOrder(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.username} - {self.order.id}"

class OrderProduct(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.order.id} - {self.product.name}"
