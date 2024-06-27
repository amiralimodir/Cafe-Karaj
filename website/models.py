from django.db import models, transaction, IntegrityError
from django.db.models import F

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
    def get_order(cls, user, product_quantities, order_type):
        with transaction.atomic():

            # inventory check
            for product_id, quantity in product_quantities:
                product = Product.objects.get(id=product_id)
                if product.sugar * quantity > Storage.objects.get(name='sugar').amount:
                    return f"Not enough sugar to make {quantity} units of {product.name}"
                if product.coffee * quantity > Storage.objects.get(name='coffee').amount:
                    return f"Not enough coffee to make {quantity} units of {product.name}"
                if product.flour * quantity > Storage.objects.get(name='flour').amount:
                    return f"Not enough flour to make {quantity} units of {product.name}"
                if product.chocolate * quantity > Storage.objects.get(name='chocolate').amount:
                    return f"Not enough chocolate to make {quantity} units of {product.name}"
            
            for product_id, quantity in product_quantities:
                product = Product.objects.get(id=product_id)
                Storage.objects.filter(name='sugar').update(amount=F('amount') - product.sugar * quantity)
                Storage.objects.filter(name='coffee').update(amount=F('amount') - product.coffee * quantity)
                Storage.objects.filter(name='flour').update(amount=F('amount') - product.flour * quantity)
                Storage.objects.filter(name='chocolate').update(amount=F('amount') - product.chocolate * quantity)

            # order
            purchase_amount = sum([Product.objects.get(id=product_id).price * quantity for product_id, quantity in product_quantities])
            order = Order.objects.create(username=user, products=product_quantities, purchase_amount=purchase_amount, type=order_type)

            UserOrder.objects.create(user=user, order=order)
            for product_id, quantity in product_quantities:
                product = Product.objects.get(id=product_id)
                for _ in range(quantity):
                    OrderProduct.objects.create(order=order, product=product)

            products_list = [(Product.objects.get(id=pid), amount) for pid, amount in order.products]

            return {
                'order_id': order.id,
                'user': {
                    'username': user.username,
                    'full_name': user.full_name,
                    'email': user.email,
                    'phone_number': user.phone_number
                },
                'products': [{'id': p.id, 'name': p.name, 'amount': amount, 'price': p.price} for p, amount in products_list],
                'purchase_amount': order.purchase_amount,
                'type': 'take away' if order.type == b'\x01' else 'dine in'
            }

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
