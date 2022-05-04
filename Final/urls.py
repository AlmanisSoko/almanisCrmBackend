"""Finale URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from FinalApp import views
from FinalApp.views import CustomerNameViewSet, FarmerNameViewSet, OrderNameViewSet, OrderByNameViewSet, \
    CustomerOnlyViewSet, FarmerOnlyViewSet, CustomerDetailViewSet

router = routers.DefaultRouter()
router.register("farmer", views.FarmerViewSet, basename="farmer")
router.register("customer", views.CustomerViewSet, basename="customer")
router.register("payments", views.PaymentsViewSet, basename="payments")
router.register("orders", views.OrdersViewSet, basename="orders")
router.register("generate_bill_api", views.GenerateBillViewSet, basename="generate_bill_api")
router.register("home_api", views.HomeApiViewSet, basename="home_api")

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/gettoken/', TokenObtainPairView.as_view(), name="gettoken"),
    path('api/refresh_token/', TokenRefreshView.as_view(), name="refresh_token"),
    path('api/customerbyname/<str:phone>', CustomerNameViewSet.as_view(), name="customerbyname"),
    path('api/customername/<str:name>', CustomerDetailViewSet.as_view(), name="customername"),
    path('api/farmerbyname/<str:name>', FarmerNameViewSet.as_view(), name="farmerbyname"),
    path('api/orderbyname/<str:customer_name>', OrderNameViewSet.as_view(), name="orderbyname"),
    path('api/ordername/<str:id>', OrderByNameViewSet.as_view(), name="ordername"),
    path('api/customeronly/', CustomerOnlyViewSet.as_view(), name="customeronly"),
    path('api/farmeronly/', FarmerOnlyViewSet.as_view(), name="farmeronly"),
]
