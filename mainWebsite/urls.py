from django.contrib import admin
from django.urls import path
from . import views

app_name='main'

urlpatterns = [
    path('', views.home, name="home"),
    path('crud/', views.temp_func, name="temp_func"),
    path('login/', views.login, name="login"),
    path('registerUser/', views.registerUser, name="registerUser"),
    path('loginUser/', views.loginUser, name="loginUser"),
    path('logoutUser/', views.logoutUser, name="logoutUser"),
    path('cart/', views.cart, name="cart"),
    path('addToCart/', views.addToCart, name="addToCart"),
    path('checkoutCartItems/', views.checkoutCartItems, name="checkoutCartItems"),
    path('shop/', views.shop, name="shop"),
    path('test/', views.test, name="test"),
    path('shop/<str:category>/', views.productsByCategory, name="productsByCategory"),
    path('shop/candleContainers/<str:category>/', views.productsBySubcategory, name="productsBySubcategory"),
    path('userprofile/<str:temp>', views.userProfile, name="userProfile"),
    path('afterCheckout/', views.afterCheckout, name="afterCheckout"),
    path('showOrders/<str:orderId>', views.showOrders, name="showOrders"),
] 