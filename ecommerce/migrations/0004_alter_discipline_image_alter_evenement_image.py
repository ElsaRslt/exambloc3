# Generated by Django 5.0.4 on 2024-09-24 06:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ecommerce', '0003_alter_discipline_image_alter_evenement_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='discipline',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='sport_images/'),
        ),
        migrations.AlterField(
            model_name='evenement',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='sport_images/'),
        ),
    ]
