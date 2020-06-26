from bootstrap_datepicker_plus import DatePickerInput
from django import forms
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.db import models
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views.generic.base import TemplateView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.views.generic.list import ListView

import django_tables2 as tables
from bill.models import Client, Facture, Fournisseur, LigneFacture
from crispy_forms.helper import FormHelper
from crispy_forms.layout import HTML, Button, Submit
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
        clients = Client.objects.all().annotate(chiffre=models.Sum(models.ExpressionWrapper(models.F('factures__lignes__qte'),output_field=models.FloatField()) * models.F('factures__lignes__produit__prix')))
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
    model = Client
    
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
