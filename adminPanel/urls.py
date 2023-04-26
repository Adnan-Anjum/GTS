from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    # Authentication and authorzation
    path('', views.adminLogin, name="adminLogin"),
    path('loginAdmin/', views.loginAdmin, name="loginAdmin"),
    path('logoutAdmin/', views.logoutAdmin, name="logoutAdmin"),
    # Dashboard
    path('adminDashboard/', views.adminDashboard, name="adminDashboard"),
    path('adminDashboardGraph/', views.adminDashboardGraph, name="adminDashboardGraph"),
    # Product pages
    path('addProduct/', views.addProduct, name="addProduct"),
    path('saveNewProduct/', views.saveNewProduct, name="saveNewProduct"),
    path('editProduct/', views.editProduct, name="editProduct"),
    path('updateProductData/', views.updateProductData, name="updateProductData"),
]