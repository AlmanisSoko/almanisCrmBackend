"""
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework import routers

from pythonApp import views
from pythonApp.views import SuperUserRegistrationView, CustomerNameViewSet, FarmerNameViewSet, OrderNameViewSet, OrderByNameViewSet, \
    CustomerOnlyViewSet, FarmerOnlyViewSet, CustomerDetailViewSet, FarmerStockNameViewSet, FarmerOnlyNameViewSet, \
     TotalPositiveBalanceView, TotalNegativeBalanceView, CustomerViewSet, TotalBalanceView, TotalPaymentView, TotalDiscountView, TotalKilosView

router = routers.DefaultRouter()
router.register("farmer", views.FarmerViewSet, basename="farmer")
router.register("customer", views.CustomerViewSet, basename="customer")
router.register("payments", views.PaymentsViewSet, basename="payments")
router.register("orders", views.OrdersViewSet, basename="orders")
router.register("generate_bill_api", views.GenerateBillViewSet, basename="generate_bill_api")
router.register("home_api", views.HomeApiViewSet, basename="home_api")
router.register("region", views.RegionViewSet, basename="region")
router.register("invoice", views.InvoiceViewSet, basename="invoice")
router.register("tickets", views.TicketViewSet, basename="tickets")
router.register("analytics", views.PKTViewSet, basename="analytics")
router.register("onlycustomer", views.OnlyCustomerViewSet, basename="onlycustomer")
router.register("stock", views.FarmerStockViewSet, basename="stock")
router.register("debtors", views.CustomersWithPositiveBalanceViewSet, basename="debtors")
router.register("overdue", views.CustomersWithNegativeBalanceViewSet, basename="overdue")
router.register("yearly_chart", views.YearlyDataView, basename="yearly_chart")
router.register("monthly_chart", views.MonthlyDataView, basename="monthly_chart")
router.register("daily_chart", views.DailyDataView, basename="daily_chart")
router.register("customers_region", views.CustomerRegionView, basename="customers_region")
router.register("payments_breakdown", views.PaymentBreakdownView, basename="payments_breakdown")
router.register("dashboard", views.DashboardView, basename="dashboard")

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.jwt')),
    path('auth/', include('djoser.urls.authtoken')),
    path('auth/', include('djoser.social.urls')),
    path('auth/superuser/', SuperUserRegistrationView.as_view({'post': 'create_superuser'}), name='superuser-registration'),
    path('api/customerbyname/<str:phone>', CustomerNameViewSet.as_view(), name="customerbyname"),
    path('api/customers/customers-with-balance/', CustomerViewSet.as_view({'get': 'customers_with_balance'}), name='customers-with-balance'),
    path('api/customers/customers-with-excess/', CustomerViewSet.as_view({'get': 'customers_with_excess'}), name='customers-with-excess'),
    path('api/customers/total-balance/', CustomerViewSet.as_view({'get': 'total_balance'}), name='total-balance'),
    path('api/customername/<str:name>', CustomerDetailViewSet.as_view(), name="customername"),
    path('api/total-balance/', TotalBalanceView.as_view(), name='total-balance'),
    path('api/total-payment/', TotalPaymentView.as_view(), name='total-payment'),
    path('api/total-discount/', TotalDiscountView.as_view(), name='total-discount'),
    path('api/total-kgs/', TotalKilosView.as_view(), name='total-kgs'),
    path('api/farmerbyname/<str:name>', FarmerNameViewSet.as_view(), name="farmerbyname"),
    path('api/orderbyname/<str:customer_name>', OrderNameViewSet.as_view(), name="orderbyname"),
    path('api/ordername/<str:id>', OrderByNameViewSet.as_view(), name="ordername"),
    path('api/customeronly/', CustomerOnlyViewSet.as_view(), name="customeronly"),
    path('api/farmeronly/', FarmerOnlyViewSet.as_view(), name="farmeronly"),
    path('api/farmername/', FarmerStockNameViewSet.as_view(), name="farmername"),
    path('api/farmerstockname/', FarmerOnlyNameViewSet.as_view(), name="farmerstockname"),
    path('api/underpaid/', TotalPositiveBalanceView.as_view(), name="underpaid"),
    path('api/overpaid/', TotalNegativeBalanceView.as_view(), name="overpaid")
]
