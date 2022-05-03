from django.contrib import admin

# Register your models here.
from FinaleApp.models import Farmer, Customer, Orders, Bill, BillDetails, Payments

admin.site.register(Farmer)
admin.site.register(Customer)
admin.site.register(Orders)
admin.site.register(Bill)
admin.site.register(BillDetails)
admin.site.register(Payments)
