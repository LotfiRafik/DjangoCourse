# Generated by Django 3.2.3 on 2021-05-17 08:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bill', '0004_facture_commande'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='first_name',
            field=models.CharField(blank=True, max_length=150, verbose_name='first name'),
        ),
    ]
