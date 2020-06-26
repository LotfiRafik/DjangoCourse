from django.db import models
from django import utils
import datetime
from django.urls import reverse
from django.db.models import Sum, F

# Create your models here.

class Client(models.Model):
    SEXE = (
        ('M', 'Masculin'),
        ('F', 'Feminin')
    )
    nom = models.CharField(max_length=50, null=True, blank=True)
    prenom = models.CharField(max_length=50, null=True, blank=True)
    adresse = models.TextField(null=True, blank=True)
    tel = models.CharField(max_length = 10, null=True, blank=True)
    sexe = models.CharField(max_length=1, choices = SEXE)
    
    def __str__(self):
        return self.nom + ' ' + self.prenom


class Fournisseur(models.Model):
    SEXE = (
        ('M', 'Masculin'),
        ('F', 'Feminin')
    )
    nom = models.CharField(max_length=50, null=True, blank=True)
    prenom = models.CharField(max_length=50, null=True, blank=True)
    adresse = models.TextField(null=True, blank=True)
    tel = models.CharField(max_length = 10, null=True, blank=True)
    sexe = models.CharField(max_length=1, choices = SEXE)
    
    def __str__(self):
        return self.nom + ' ' + self.prenom
    
class Categorie(models.Model):
    nom = models.CharField(max_length=50)
    
    def __str__(self):
        return self.nom   

class Produit(models.Model):
    designation = models.CharField(max_length=50)
    prix = models.FloatField(default=0)
    fournisseur = models.ForeignKey(Fournisseur,on_delete=models.CASCADE,related_name='produits',null=True)
    categorie = models.ForeignKey(Categorie,on_delete=models.CASCADE,related_name='produits',null=True)
    def __str__(self):
        return self.designation

    
class Facture(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='factures')
    date = models.DateField(default=utils.timezone.now)
    def get_absolute_url(self):
        return reverse('facture_detail', kwargs={'pk': self.id})

    def __str__(self):
        return str(self.client)+' : '+ str(self.date)
    
    def total(self):
        return self.lignes.all().aggregate(total=Sum(F("produit__prix") * F("qte"),output_field=models.FloatField()))

class LigneFacture(models.Model):
    produit = models.ForeignKey(Produit, on_delete=models.CASCADE,related_name="lignes")
    qte = models.IntegerField(default=1)
    facture = models.ForeignKey(Facture, on_delete=models.CASCADE, related_name='lignes')
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['produit', 'facture'], name="produit-facture")
        ]
    