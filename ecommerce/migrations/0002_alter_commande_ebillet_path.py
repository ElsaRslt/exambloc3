# Generated by Django 5.0.4 on 2024-09-23 12:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ecommerce', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='commande',
            name='ebillet_path',
            field=models.TextField(blank=True, null=True),
        ),
    ]
