from bootstrap_datepicker_plus import DatePickerInput
from django import forms
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from django.contrib.messages.views import SuccessMessageMixin
from django.db import models
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views.generic.base import TemplateView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.views.generic.list import ListView

import django_tables2 as tables
from bill.models import (Admin, Client, Commande, Facture, Fournisseur,
                         LigneCommande, LigneFacture, Produit, User)
from crispy_forms.helper import FormHelper
from crispy_forms.layout import HTML, Button, Submit
from django_select2 import forms as s2forms
from django_tables2.config import RequestConfig

# Create your views here.

def facture_detail_view(request, pk):
    facture = get_object_or_404(Facture, id=pk)
    context={}
    context['facture'] = facture
    return render(request, 'bill/facture_detail.html', context)

class FactureUpdate(SuccessMessageMixin, UpdateView):
    model = Facture
    fields = ['client', 'date']
    template_name = 'bill/update.html'
    success_message = "La facture a été mise à jour avec succès"
    
    def get_form(self, form_class=None):
        messages.warning(self.request, "Attention, vous allez modifier la facture")
        form = super().get_form(form_class)
        form.helper = FormHelper()
        form.helper.add_input(Submit('submit','Modifier', css_class='btn-warning'))
        form.helper.add_input(Button('cancel', 'Annuler', css_class='btn-secondary', onclick="window.history.back()"))
        self.success_url = reverse('facture_table_detail', kwargs={'pk':self.kwargs.get('pk')})
        return form


class LigneFactureTable(tables.Table):
    action= '<a href="{% url "lignefacture_update" pk=record.id facture_pk=record.facture.id %}" class="btn btn-warning">Modifier</a>\
            <a href="{% url "lignefacture_delete" pk=record.id facture_pk=record.facture.id %}" class="btn btn-danger">Supprimer</a>'
    edit   = tables.TemplateColumn(action)    
    class Meta:
        model = LigneFacture
        template_name = "django_tables2/bootstrap4.html"
        fields = ('produit__designation','produit__id', 'produit__prix', 'qte' )


class FactureDetailView(DetailView):
    template_name = 'bill/facture_table_detail.html'
    model = Facture
    
    def get_context_data(self, **kwargs):
        context = super(FactureDetailView, self).get_context_data(**kwargs)
        
        table = LigneFactureTable(LigneFacture.objects.filter(facture=self.kwargs.get('pk')))
        RequestConfig(self.request, paginate={"per_page": 2}).configure(table)
        context['table'] = table
        return context

class LigneFactureCreateView(CreateView):
    model = LigneFacture
    template_name = 'bill/create.html'
    fields = ['facture', 'produit', 'qte']
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.helper = FormHelper()

        form.fields['facture']=forms.ModelChoiceField(queryset=Facture.objects.filter(id=self.kwargs.get('facture_pk')), initial=0)
        form.helper.add_input(Submit('submit','Créer', css_class='btn-primary'))
        form.helper.add_input(Button('cancel', 'Annuler', css_class='btn-secondary', onclick="window.history.back()"))
        self.success_url = reverse('facture_table_detail', kwargs={'pk':self.kwargs.get('facture_pk')})
        return form

class LigneFactureUpdateView(UpdateView):
    model = LigneFacture
    template_name = 'bill/update.html'
    fields = ['facture', 'produit', 'qte']
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.helper = FormHelper()

        form.fields['facture']=forms.ModelChoiceField(queryset=Facture.objects.filter(id=self.kwargs.get('facture_pk')), initial=0)
        form.helper.add_input(Submit('submit','Modifier', css_class='btn-primary'))
        form.helper.add_input(Button('cancel', 'Annuler', css_class='btn-secondary', onclick="window.history.back()"))
        self.success_url = reverse('facture_table_detail', kwargs={'pk':self.kwargs.get('facture_pk')})
        return form

class LigneFactureDeleteView(DeleteView):
    model = LigneFacture
    template_name = 'bill/delete.html'
    
    def get_success_url(self):
        self.success_url = reverse('facture_table_detail', kwargs={'pk':self.kwargs.get('facture_pk')})

        



#Dashboard 
#django_tables2 fournisseur table
class FournisseurChiffreTable(tables.Table):

    chiffre = tables.Column("Chiffre-Fournisseur") # Any attr will do, dont mind it
    nom = tables.Column("Nom-Fournisseur") # Any attr will do, dont mind it
    prenom = tables.Column("Prénom-Fournisseur") # Any attr will do, dont mind it
    class Meta:
        template_name = "django_tables2/bootstrap4.html"


#django_tables2 client table
class ClientChiffreTable(tables.Table):

    #Chiffre column qui affiche la somme des totaux de toutes les factures d'un client
    nom = tables.Column("Nom-Client") # Any attr will do, dont mind it
    prenom = tables.Column("Prénom-Client") # Any attr will do, dont mind it
    chiffre = tables.Column("Chiffre-Client") # Any attr will do, dont mind it

    class Meta:
        template_name = "django_tables2/bootstrap4.html"

def dashboard(request):
    context = {}

    #fournisseurs = Fournisseur.objects.all().annotate(chiffre=models.Sum(models.ExpressionWrapper(models.F('produits__lignes__qte'),output_field=models.FloatField()) * models.F('produits__lignes__produit__prix')))
    #Chiffre d'affaire par client
    clients = LigneFacture.objects.all().values('facture__client').annotate(chiffre=models.Sum(models.ExpressionWrapper(models.F('qte'),output_field=models.FloatField()) * models.F('produit__prix')),nom=models.F('facture__client__nom'),prenom=models.F('facture__client__prenom')).order_by('-chiffre')
    table = ClientChiffreTable(clients)
    RequestConfig(request, paginate={"per_page": 8}).configure(table)
    context['table_client'] = table

    #Chiffre d'affaire par fournisseur
    fournisseurs = LigneFacture.objects.all().values('produit__fournisseur').annotate(chiffre=models.Sum(models.ExpressionWrapper(models.F('qte'),output_field=models.FloatField()) * models.F('produit__prix')),nom=models.F('produit__fournisseur__nom'),prenom=models.F('produit__fournisseur__prenom'))
    table = FournisseurChiffreTable(fournisseurs)
    RequestConfig(request, paginate={"per_page": 8}).configure(table)
    context['table_fournisseur'] = table

    labels = []
    data = []

    #Chiffre d'affaire par jour
    factures = Facture.objects.all().values('date').annotate(total=models.Sum(models.F("lignes__produit__prix") * models.F("lignes__qte"),output_field=models.FloatField()))    
    for f in factures:
        labels.append(str(f['date']))
        data.append(f['total'])
    context['labelsLine'] = labels
    context['dataLine'] = data

    labels = []
    data = []
    #Chiffre par categorie de produit 
    produits = LigneFacture.objects.all().values('produit__categorie').annotate(total=models.Sum(models.F("produit__prix") * models.F("qte"),output_field=models.FloatField()),Categorie=models.F("produit__categorie__nom"))
    for f in produits:
        labels.append(f['Categorie'])
        data.append(f['total'])
    print(labels,data)
    context['labelsRadar'] = labels
    context['dataRadar'] = data

    return render(request, 'bill/dashboard.html',context)


        

#django_tables2 client table
class ClientTable(tables.Table):

    #Chiffre column qui affiche la somme des totaux de toutes les factures d'un client
    chiffre = tables.Column("Chiffre") # Any attr will do, dont mind it

    modifier = '<a href="{% url "client_update" pk=record.id  %}" class="btn btn-warning">Modifier</a>'
    suprimer = '<a href="{% url "client_delete" pk=record.id %}" class="btn btn-danger">Supprimer</a>'
    factures = '<a href="{% url "client_table_detail" pk=record.id %}" class="btn btn-info">Factures</a>'
    edit   = tables.TemplateColumn(modifier) 
    delete   = tables.TemplateColumn(suprimer) 
    Factures   = tables.TemplateColumn(factures) 

    
    class Meta:
        model = Client
        template_name = "django_tables2/bootstrap4.html"
        fields = ('nom','prenom', 'adresse', 'tel' , 'sexe' )

#Client list view 
class ClientListView(ListView):
    template_name = 'bill/list.html'
    model = Client
    
    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)
        #Total chiffre d'affaire de chaque client
        clients = Client.objects.filter().annotate(chiffre=models.Sum(models.ExpressionWrapper(models.F('factures__lignes__qte'),output_field=models.FloatField()) * models.F('factures__lignes__produit__prix')))
        table = ClientTable(clients)
        RequestConfig(self.request, paginate={"per_page": 8}).configure(table)
        context['table'] = table
        #URL qui pointe sur la vue de création
        context['creation_url']  = "/bill/client_table_create/"
        context['object'] = 'Client'
        context['title'] = 'La liste des clients :'

        return context


class ClientCreateView(CreateView):
    model = Client
    template_name = 'bill/create.html'
    fields = '__all__'
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.helper = FormHelper()

        form.helper.add_input(Submit('submit','Créer', css_class='btn-primary'))
        form.helper.add_input(Button('cancel', 'Annuler', css_class='btn-secondary', onclick="window.history.back()"))
        self.success_url = reverse('clients')
        return form

    def form_valid(self, form):
        self.object = form.save()
        user = self.object.user
        user.user_type = 1
        user.save()
        return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        ctx = super(ClientCreateView, self).get_context_data(**kwargs)
        ctx['object'] = 'Client'
        ctx['title'] = "Création d'un client :"
        return ctx


class ClientUpdateView(UpdateView):
    model = Client
    template_name = 'bill/update.html'
    fields = '__all__'
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.helper = FormHelper()

        form.helper.add_input(Submit('submit','Modifier', css_class='btn-primary'))
        form.helper.add_input(Button('cancel', 'Annuler', css_class='btn-secondary', onclick="window.history.back()"))
        self.success_url = reverse('clients')
        return form
    
    def get_context_data(self, **kwargs):
        ctx = super(ClientUpdateView, self).get_context_data(**kwargs)
        ctx['object'] = 'Client'
        ctx['title'] = "Modification du client : " + str(self.get_object())
        return ctx


class ClientDeleteView(DeleteView):
    model = Client
    template_name = 'bill/delete.html'
    
    def get_success_url(self):
        success_url = reverse('clients')
        return success_url


class FactureTable(tables.Table):

    #Total de la facture
    total = tables.Column("Total") # Any attr will do, dont mind it

    modifier = '<a href="{% url "facture_update" pk=record.id  %}" class="btn btn-warning">Modifier</a>'
    lignes =   '<a href="{% url "facture_table_detail" pk=record.id  %}" class="btn btn-info">Lignes</a>'
    edit   = tables.TemplateColumn(modifier) 
    Lignes   = tables.TemplateColumn(lignes)  
 

    class Meta:
        model = Facture
        template_name = "django_tables2/bootstrap4.html"
        fields = ('client','date')


class ClientDetailView(DetailView):
    template_name = 'bill/list.html'
    model = Client
    
    def get_context_data(self, **kwargs):
        context = super(ClientDetailView, self).get_context_data(**kwargs)
        
        table = FactureTable(Facture.objects.filter(client=self.kwargs.get('pk')).annotate(total=models.Sum(models.F("lignes__produit__prix") * models.F("lignes__qte"),output_field=models.FloatField())))
        RequestConfig(self.request, paginate={"per_page": 5}).configure(table)
        context['table'] = table
        #URL qui pointe sur la vue de création
        context['creation_url']  = "/bill/facture_create/" + str(self.kwargs.get('pk')) + "/"
        context['object'] = 'Facture'
        context['title'] = 'La liste des factures du client ' + str(self.get_object())

        return context


class FactureCreateView(CreateView):
    model = Facture
    template_name = 'bill/create.html'
    fields = '__all__'
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.helper = FormHelper()

        form.fields['date'] = forms.DateField(widget=DatePickerInput(format='%m/%d/%Y'))
        form.fields['client']=forms.ModelChoiceField(queryset=Client.objects.filter(id=self.kwargs.get('client_pk')), initial=0)
        form.helper.add_input(Submit('submit','Créer', css_class='btn-primary'))
        form.helper.add_input(Button('cancel', 'Annuler', css_class='btn-secondary', onclick="window.history.back()"))
        self.success_url = reverse('client_table_detail', kwargs={'pk':self.kwargs.get('client_pk')})
        return form

    def get_context_data(self, **kwargs):
        ctx = super(FactureCreateView, self).get_context_data(**kwargs)
        ctx['object'] = 'Facture'
        ctx['title'] = "Création d'une facture :"

        return ctx

#-----------------------------------------------------------------------------------------------------------------------------------------------------------
# fournisseur table , updateview , deleteview , createview , listview + modify urls
#-----------------------------------------------------------------------------------------------------------------------------------------------------------

#django_tables2 fournisseur table
class FournisseurTable(tables.Table):

    modifier = '<a href="{% url "fournisseur_update" pk=record.id  %}" class="btn btn-warning">Modifier</a>'
    suprimer = '<a href="{% url "fournisseur_delete" pk=record.id %}" class="btn btn-danger">Supprimer</a>'
    edit   = tables.TemplateColumn(modifier) 
    delete   = tables.TemplateColumn(suprimer) 

    class Meta:
        model = Fournisseur
        template_name = "django_tables2/bootstrap4.html"
        fields = ('nom','prenom', 'adresse', 'tel' , 'sexe' )



#Fournisseur list view 
class FournisseurListView(ListView):
    template_name = 'bill/list.html'
    model = Fournisseur
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        #Total chiffre d'affaire de chaque client
        fournisseurs = Fournisseur.objects.all()
        table = FournisseurTable(fournisseurs)
        RequestConfig(self.request, paginate={"per_page": 8}).configure(table)
        context['table'] = table
        #URL qui pointe sur la vue de création
        context['creation_url']  = "/bill/fournisseur_table_create/"
        context['object'] = 'fournisseur'
        context['title'] = 'La liste des fournisseurs :'

        return context


class FournisseurCreateView(CreateView):
    model = Fournisseur
    template_name = 'bill/create.html'
    fields = '__all__'
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.helper = FormHelper()

        form.helper.add_input(Submit('submit','Créer', css_class='btn-primary'))
        form.helper.add_input(Button('cancel', 'Annuler', css_class='btn-secondary', onclick="window.history.back()"))
        self.success_url = reverse('fournisseurs')
        return form

    def form_valid(self, form):
        self.object = form.save()
        user = self.object.user
        user.user_type = 2
        user.save()
        return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        ctx = super(FournisseurCreateView, self).get_context_data(**kwargs)
        ctx['object'] = 'fournisseur'
        ctx['title'] = "Création d'un fournisseur :"
        return ctx


class FournisseurUpdateView(UpdateView):
    model = Fournisseur
    template_name = 'bill/update.html'
    fields = '__all__'
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.helper = FormHelper()

        form.helper.add_input(Submit('submit','Modifier', css_class='btn-primary'))
        form.helper.add_input(Button('cancel', 'Annuler', css_class='btn-secondary', onclick="window.history.back()"))
        self.success_url = reverse('fournisseurs')
        return form
    
    def get_context_data(self, **kwargs):
        ctx = super(FournisseurUpdateView, self).get_context_data(**kwargs)
        ctx['object'] = 'fournisseur'
        ctx['title'] = "Modification du fournisseur : " + str(self.get_object())
        return ctx

class FournisseurDetailView(DetailView):
    template_name = 'bill/list.html'
    model = Client
    
    def get_context_data(self, **kwargs):
        context = super(FournisseurDetailView, self).get_context_data(**kwargs)
        
        table = FactureTable(Facture.objects.filter(fournisseur=self.kwargs.get('pk')))
        RequestConfig(self.request, paginate={"per_page": 5}).configure(table)
        context['table'] = table
        #URL qui pointe sur la vue de création
        context['creation_url']  = "/bill/facture_create/" + str(self.kwargs.get('pk')) + "/"
        context['object'] = 'fournisseur detail'
        context['title'] = 'detail fournisseur ' + str(self.get_object())

        return context

class FournisseurtDeleteView(DeleteView):
    model = Fournisseur
    template_name = 'bill/delete.html'
    
    def get_success_url(self):
        success_url = reverse('fournisseurs')
        return success_url


#-----------------------------------------------------------------------------------------------------------------------------------------------------------
# produit table , updateview , deleteview , createview , listview + modify urls
#--------


#django_tables2 produit table
class ProduitTable(tables.Table):

    add_panier =   '<a href="{% url "add_produit_panier" pk=record.id %}" class="btn btn-info">Ajouter</a>'
    photo =   '<img src="{{ record.photo.url }}" alt="produit" width="200" height="200">'
    photo   = tables.TemplateColumn(photo) 

    Panier   = tables.TemplateColumn(add_panier) 

    class Meta:
        model = Produit
        template_name = "django_tables2/bootstrap4.html"
        fields = ('designation','categorie', 'prix')


class ProduitForm(forms.ModelForm):
    class Meta:
        model = Produit
        fields = ("designation","categorie")
        widgets = {
            'designation': s2forms.Select2Widget,
            'categorie': s2forms.Select2Widget
        }

#Produit list view 
class ProduitListView(ListView):
    template_name = 'bill/list.html'
    model = Produit
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        produits = Produit.objects.all()
        table = ProduitTable(produits)
        RequestConfig(self.request, paginate={"per_page": 5}).configure(table)
        pform = ProduitForm()
        context['pform'] = pform
        context['table'] = table
        #URL qui pointe sur la vue de création
        context['creation_url']  = "/bill/produit_table_create/"
        context['object'] = 'produit'
        context['title'] = 'La liste des produits :'

        return context


class ProduitCreateView(CreateView):
    model = Produit
    template_name = 'bill/create.html'
    fields = '__all__'
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.helper = FormHelper()

        form.helper.add_input(Submit('submit','Créer', css_class='btn-primary'))
        form.helper.add_input(Button('cancel', 'Annuler', css_class='btn-secondary', onclick="window.history.back()"))
        self.success_url = reverse('produits')
        return form

    def get_context_data(self, **kwargs):
        ctx = super(ProduitCreateView, self).get_context_data(**kwargs)
        ctx['object'] = 'Produit'
        ctx['title'] = "Création d'un Produit :"
        return ctx


@login_required
def ajouter_panier_view(request, pk):

    context={}
    if request.method == 'GET':
        #return detail of the product and input to enter the qte of the product , butom submit
        produit = get_object_or_404(Produit, id=pk)
        context['produit'] = produit
        return render(request, 'bill/ajouter_produit_panier.html', context)
    elif request.method == 'POST':
        #update panier (session)
        produit = get_object_or_404(Produit, id=pk)
        if 'qte' not in request.POST:
            qte = 1
        else:
            qte = int(request.POST['qte'])
            if qte < 0:
                qte = 1
        
        if 'panier' not in request.session:
            request.session['panier'] = {}
        request.session['panier'][int(pk)] = qte
        request.session.modified = True
        return HttpResponseRedirect(reverse('produits'))


#django_tables2 panier table
class PanierTable(tables.Table):

    produit = tables.Column()
    qte = tables.Column()

    class Meta:
        template_name = "django_tables2/bootstrap4.html"
        fields = ('produit','qte')

@login_required
def panier_detail_view(request):
    panier = []
    context = {}
    
    if 'panier' in request.session:
        for pk,qte in request.session['panier'].items():
            produit = get_object_or_404(Produit, id=pk)
            panier.append({"produit":produit,"qte":qte})

    table = PanierTable(panier)
    RequestConfig(request, paginate={"per_page": 5}).configure(table)
    context['table'] = table

    return render(request, 'bill/panier.html', context)


@login_required
def confirme_panier_view(request):

    if 'panier' in request.session and len(request.session['panier']) > 0:
        commande = Commande.objects.create(client=request.user.client)
        for pk,qte in request.session['panier'].items():
            produit = get_object_or_404(Produit, id=pk)
            LigneCommande.objects.create(produit=produit,qte=qte,commande=commande)
        request.session['panier'] = {}
        request.session.modified = True
    return HttpResponseRedirect(reverse('commandes'))

        

#django_tables2 client table
class CommandeTable(tables.Table):

    lignes = '<a href="{% url "commande_table_detail" pk=record.id %}" class="btn btn-info">Lignes</a>'
    Lignes   = tables.TemplateColumn(lignes) 

    class Meta:
        model = Commande
        template_name = "django_tables2/bootstrap4.html"
        fields = ('client','date', 'valide')

class CommandeTableAdmin(CommandeTable):

    valider = '<a href="{% url "valider_commande" pk=record.id %}" class="btn btn-info">Valider </a>'
    valider   = tables.TemplateColumn(valider) 
    class Meta:
        model = Commande
        template_name = "django_tables2/bootstrap4.html"
        fields = ('client','date', 'valide')

#Commande list view 
class CommandeListView(ListView):
    
    template_name = 'bill/commandes.html'
    model = Commande
    
    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        filter = {}
        if self.request.user.is_authenticated:
            if self.request.user.user_type == 1:
                filter['client'] = self.request.user.client
        commandes = Commande.objects.filter(**filter)

        if self.request.user.user_type == 0:
            table = CommandeTableAdmin(commandes)
        elif self.request.user.user_type == 1:
            table = CommandeTable(commandes)

        RequestConfig(self.request, paginate={"per_page": 8}).configure(table)
        context['table'] = table
        context['object'] = 'Commande'
        context['title'] = 'La liste des commandes :'

        return context



class LigneCommandeTable(tables.Table):
    class Meta:
        model = LigneCommande
        template_name = "django_tables2/bootstrap4.html"
        fields = ('produit__designation','produit__id', 'produit__prix', 'qte')



class CommandeDetailView(DetailView):
    template_name = 'bill/commandes.html'
    model = Commande
    
    def get_context_data(self, **kwargs):
        context = super(CommandeDetailView, self).get_context_data(**kwargs)
        commande = Commande.objects.get(id=self.kwargs.get('pk'))
        table = LigneCommandeTable(LigneCommande.objects.filter(commande=commande))
        RequestConfig(self.request, paginate={"per_page": 5}).configure(table)
        context['table'] = table
        context['object'] = 'LigneCommande'
        context['title'] = 'La liste des produits de la commande : ' + str(self.get_object())

        return context



@login_required
def valider_commande_view(request, pk):
    try:
        commande = Commande.objects.filter(id=pk)
    except Commande.DoesNotExist:
        raise Http404
    if commande[0].valide == False:
        commande.update(valide = True)
        commande = commande[0]
        facture = Facture.objects.create(client=commande.client,commande=commande)
        for ligne in commande.lignes.all():
            LigneFacture.objects.create(produit=ligne.produit,qte=ligne.qte,facture=facture)

    return HttpResponseRedirect(reverse('commandes'))


class AuthorWidget(s2forms.Select2Widget):
    search_fields = [
        "username__icontains",
        "email__icontains",
    ]


class ProduitCreateView(ListView):
    model = Produit
    form_class = ProduitForm
    success_url = "/"
