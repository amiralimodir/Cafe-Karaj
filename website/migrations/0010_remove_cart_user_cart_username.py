# Generated by Django 4.2.13 on 2024-07-03 08:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0009_cart'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cart',
            name='user',
        ),
        migrations.AddField(
            model_name='cart',
            name='username',
            field=models.CharField(default=0, max_length=255),
            preserve_default=False,
        ),
    ]
