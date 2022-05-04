from django.db import models


# Create your models here.
class Farmer(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=255)
    added_on = models.DateTimeField(auto_now_add=True)
    objects = models.Manager()


class Customer(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=255)
    town = models.CharField(max_length=255)
    region = models.CharField(max_length=255)
    added_on = models.DateTimeField(auto_now_add=True)
    objects = models.Manager()


class Orders(models.Model):
    choices = ((1, "Nairobi"), (2, "Nyanza"),
               (3, "Central"), (4, "Coast"),
               (5, "Eastern"), (6, "North Eastern"),
               (7, "Western"), (8, "Rift Valley"))

    id = models.AutoField(primary_key=True)
    phone = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    customer_id = models.ForeignKey(Customer, on_delete=models.CASCADE)
    town = models.CharField(max_length=255)
    region = models.CharField(choices=choices, max_length=255)
    farmer_id = models.ForeignKey(Farmer, on_delete=models.CASCADE)
    kgs = models.CharField(max_length=255)
    packaging = models.CharField(max_length=255)
    transport = models.CharField(max_length=255)
    discount = models.CharField(max_length=255)
    amount = models.CharField(max_length=255)
    price = models.CharField(max_length=255)
    comment = models.TextField()
    status = models.BooleanField(default=False)
    added_on = models.DateTimeField(auto_now_add=True)
    objects = models.Manager()


class Payments(models.Model):
    choices = ((1, "Cash"), (2, "Mpesa"))

    id = models.AutoField(primary_key=True)
    orders_id = models.ForeignKey(Orders, on_delete=models.CASCADE)
    paying_number = models.CharField(max_length=255)
    amount = models.CharField(max_length=255)
    payment_mode = models.CharField(choices=choices, max_length=255)
    payment = models.CharField(max_length=255)
    balance = models.CharField(max_length=255)
    customer_id = models.ForeignKey(Customer, on_delete=models.CASCADE)
    added_on = models.DateTimeField(auto_now_add=True)
    objects = models.Manager()


class CustomerBill(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=255)
    added_on = models.DateTimeField(auto_now_add=True)
    objects = models.Manager()


class Bill(models.Model):
    id = models.AutoField(primary_key=True)
    customerbill_id = models.ForeignKey(CustomerBill, on_delete=models.CASCADE)
    added_on = models.DateTimeField(auto_now_add=True)
    objects = models.Manager()


class BillDetails(models.Model):
    id = models.AutoField(primary_key=True)
    bill_id = models.ForeignKey(Bill, on_delete=models.CASCADE)
    order_id = models.ForeignKey(Orders, on_delete=models.CASCADE)
    added_on = models.DateTimeField(auto_now_add=True)
    objects = models.Manager()
