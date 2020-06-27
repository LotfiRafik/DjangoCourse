from django.contrib import admin
from bill.models import Client, Produit, Facture,Commande, LigneCommande, LigneFacture, Fournisseur, Categorie, User, Admin

# Register your models here.
admin.site.register(User)
admin.site.register(Admin)
admin.site.register(Client)
admin.site.register(Facture)
admin.site.register(Produit)
admin.site.register(LigneFacture)
admin.site.register(Fournisseur)
admin.site.register(Categorie)
admin.site.register(Commande)
admin.site.register(LigneCommande)