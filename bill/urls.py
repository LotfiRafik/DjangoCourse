from django.urls import  path, re_path, include
from bill import views
urlpatterns = [
    re_path(r'^facture_detail/(?P<pk>\d+)/$', views.facture_detail_view, name='facture_detail'),

    #Detail d'une facture (La liste des lignes de facture)
    re_path(r'^facture_table_detail/(?P<pk>\d+)/$', views.FactureDetailView.as_view(), name='facture_table_detail'),
    #Creation d'une ligne de facture
    re_path(r'^lignefacture_table_create/(?P<facture_pk>\d+)/$', views.LigneFactureCreateView.as_view(), name='facture_table_create'),
    #Supression d'une ligne de facture
    re_path(r'^lignefacture_delete/(?P<pk>\d+)/(?P<facture_pk>\d+)/$', views.LigneFactureDeleteView.as_view(), name='lignefacture_delete'),
    #Modification d'une ligne de facture
    re_path(r'^lignefacture_update/(?P<pk>\d+)/(?P<facture_pk>\d+)/$', views.LigneFactureUpdateView.as_view(), name='lignefacture_update'),
    
    #Modification d'une facture
    re_path(r'^facture_update/(?P<pk>\d+)/$', views.FactureUpdate.as_view(), name='facture_update'),
    #Creation d'une facture
    path('facture_create/<int:client_pk>/', views.FactureCreateView.as_view(), name='facture_create'),

    #Liste des clients
    path('clients/', views.ClientListView.as_view(), name='clients'),
    #Detail d'un client (Les factures de ce client)
    path('client_table_detail/<int:pk>/', views.ClientDetailView.as_view(), name='client_table_detail'),
    #Creation d'un client
    path('client_table_create/', views.ClientCreateView.as_view(), name='client_table_create'),
    #Modification d'un client
    path('client_update/<int:pk>/', views.ClientUpdateView.as_view(), name='client_update'),
    #Supression d'un client
    path('client_delete/<int:pk>/', views.ClientDeleteView.as_view(), name='client_delete'),


    #Liste des Fournisseurs
    path('fournisseurs/', views.FournisseurListView.as_view(), name='fournisseurs'),
    
  
    #Creation d'un fournisseur
    path('fournisseur_table_create/', views.FournisseurCreateView.as_view(), name='fournisseur_table_create'),
    #Modification d'un fournisseur
    path('fournisseur_update/<int:pk>/', views.FournisseurUpdateView.as_view(), name='fournisseur_update'),
    #Supression d'un fournisseur
    path('fournisseur_delete/<int:pk>/', views.FournisseurtDeleteView.as_view(), name='fournisseur_delete'),

    #Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),

]