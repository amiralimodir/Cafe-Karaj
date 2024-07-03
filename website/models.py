from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models, transaction, IntegrityError
from django.db.models import F
import json

class User(AbstractUser):
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=15)

    groups = models.ManyToManyField(
        Group,
        related_name='website_user_set',  # Specify a custom related name
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups'
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='website_user_set',  # Specify a custom related name
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions'
    )

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', 'full_name', 'phone_number']

class Product(models.Model):
    VERTICAL_CHOICES = [
        ('cold_drinks', 'Cold Drinks'),
        ('hot_drinks', 'Hot Drinks'),
        ('cake', 'Cake'),
        ('shake', 'Shake'),
    ]

    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    sugar = models.IntegerField(default=0)
    coffee = models.IntegerField(default=0)
    flour = models.IntegerField(default=0)
    egg = models.IntegerField(default=0)
    milk = models.IntegerField(default=0)
    chocolate = models.IntegerField()
    vertical_type = models.CharField(max_length=50, choices=VERTICAL_CHOICES, default='hot_drinks')
    price = models.IntegerField()
    image = models.ImageField(upload_to='products_images/')

    def __str__(self):
        return self.name
    
    @classmethod
    def add_product(cls, name, sugar, coffee, flour, egg, milk, chocolate, vertical_type, price, image):
        product = cls(
            name=name,
            sugar=sugar,
            coffee=coffee,
            flour=flour,
            egg=egg,
            milk=milk,
            chocolate=chocolate,
            vertical_type=vertical_type,
            price=price,
            image=image
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
            if product.milk > 0:
                possible_counts.append(storage.get('milk', 0) // product.milk)
            if product.egg > 0:
                possible_counts.append(storage.get('egg', 0) // product.egg)
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
            Storage.objects.filter(name='floor').update(amount=models.F('amount') - product.flour * quantity)
            Storage.objects.filter(name='milk').update(amount=models.F('amount') - product.milk * quantity)
            Storage.objects.filter(name='egg').update(amount=models.F('amount') - product.egg * quantity)
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


class Cart(models.Model):
    username = models.CharField(max_length=255)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f'{self.product.name} (x{self.quantity})'
    


sugar, created = Storage.objects.get_or_create(name='sugar', defaults={'amount': 0})
coffee, created = Storage.objects.get_or_create(name='coffee', defaults={'amount': 0})
floor, created = Storage.objects.get_or_create(name='floor', defaults={'amount': 0})
milk, created = Storage.objects.get_or_create(name='milk', defaults={'amount': 0})
egg, created = Storage.objects.get_or_create(name='egg', defaults={'amount': 0})
chocolate, created = Storage.objects.get_or_create(name='chocolate', defaults={'amount': 0})
    