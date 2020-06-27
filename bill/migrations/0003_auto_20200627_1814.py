# Generated by Django 3.0.6 on 2020-06-27 18:14

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('bill', '0002_auto_20200626_1934'),
    ]

    operations = [
        migrations.CreateModel(
            name='Commande',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(default=django.utils.timezone.now)),
                ('valide', models.BooleanField(default=False)),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='commandes', to='bill.Client')),
            ],
        ),
        migrations.AddField(
            model_name='produit',
            name='photo',
            field=models.ImageField(default=None, upload_to=''),
        ),
        migrations.CreateModel(
            name='LigneCommande',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('qte', models.IntegerField(default=1)),
                ('commande', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='lignes', to='bill.Commande')),
                ('produit', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='lignes_commande', to='bill.Produit')),
            ],
        ),
        migrations.AddConstraint(
            model_name='lignecommande',
            constraint=models.UniqueConstraint(fields=('produit', 'commande'), name='produit-commande'),
        ),
    ]