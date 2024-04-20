from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db.models.signals import pre_save
from django.dispatch import receiver


class UserAccountManager(BaseUserManager):
    def create_user(self, email, first_name, last_name, phone, password=None, user_type=None):
        if not email:
            raise ValueError('Users must have an email address')

        email = self.normalize_email(email)
        email = email.lower()

        user = self.model(
            email=email,
            first_name=first_name,
            last_name=last_name,
            user_type=user_type,
            phone=phone
        )

        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, first_name,  last_name, phone, user_type=None, password=None):
        user = self.create_user(email, first_name, last_name, phone, user_type, password)

        user.is_superuser = True
        user.is_staff = True

        user.save(using=self._db)

        return user


class UserAccount(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(max_length=255, unique=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=255)
    user_type = models.CharField(max_length=20, default='normal')
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserAccountManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'phone', 'user_type']

    def __str__(self):
        return self.email


class Farmer(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=255)
    added_on = models.DateTimeField(auto_now_add=True)
    objects = models.Manager()


class Customer(models.Model):
    choices = ((1, "Nairobi"), (2, "Nyanza"),
               (3, "Central"), (4, "Coast"),
               (5, "Eastern"), (6, "North Eastern"),
               (7, "Western"), (8, "Rift Valley"))

    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    phone = models.CharField(unique=True, max_length=255)
    secondary_phone = models.CharField(max_length=255, default=0, editable=True)
    alternative_phone = models.CharField(max_length=255, default=0, editable=True)
    town = models.CharField(max_length=255)
    region = models.CharField(choices=choices, max_length=255)
    added_on = models.DateTimeField(auto_now_add=True)
    objects = models.Manager()


class Orders(models.Model):
    choices1 = ((1, "Pishori"), (2, "Komboka"), (3, "Brown"))
    choices = ((1, "Others"), (2, "In-house"))

    id = models.AutoField(primary_key=True)
    phone = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    customer_id = models.ForeignKey(Customer, on_delete=models.CASCADE)
    town = models.CharField(max_length=255)
    farmer_id = models.ForeignKey(Farmer, on_delete=models.CASCADE)
    user_id = models.ForeignKey(UserAccount, on_delete=models.CASCADE, blank=True, null=True)
    kgs = models.CharField(max_length=255)
    packaging = models.CharField(max_length=255)
    transport = models.CharField(max_length=255)
    transporters = models.CharField(choices=choices, max_length=255)
    rider = models.CharField(max_length=255, default=0, editable=True)
    vat = models.CharField(max_length=255, default=0, editable=True)
    discount = models.CharField(max_length=255)
    amount = models.CharField(max_length=255)
    farmer_price = models.CharField(max_length=255, default=180, editable=True)
    price = models.CharField(max_length=255)
    comment = models.TextField()
    rice_type = models.CharField(choices=choices1, max_length=255)
    status = models.BooleanField(default=False)
    added_on = models.DateTimeField(auto_now_add=True)
    objects = models.Manager()


class Payments(models.Model):
    choices = ((1, "Cash"), (2, "Mpesa"), (3, "Bank"), (4, "Barter Trade"), (5, "Promo"), (6, "Compensation"), (7, "Top-up"))

    id = models.AutoField(primary_key=True)
    orders_id = models.ForeignKey(Orders, on_delete=models.CASCADE)
    paying_number = models.CharField(max_length=255)
    amount = models.CharField(max_length=255)
    payment_mode = models.CharField(choices=choices, max_length=255)
    payment = models.CharField(max_length=255)
    customer_id = models.ForeignKey(Customer, on_delete=models.CASCADE)
    added_on = models.DateTimeField(auto_now_add=True)
    objects = models.Manager()


# Define a signal receiver function to update payments when the customer of an order is changed
@receiver(pre_save, sender=Orders)
def update_payments_on_customer_change(sender, instance, **kwargs):
    if instance.pk:
        try:
            old_instance = sender.objects.get(pk=instance.pk)
            if old_instance.customer_id != instance.customer_id:
                # Customer has been changed, update associated payments
                Payments.objects.filter(orders_id=instance).update(customer_id=instance.customer_id)
        except sender.DoesNotExist:
            pass


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


class MpesaCalls(models.Model):
    ip_address = models.TextField()
    caller = models.TextField()
    conversation_id = models.TextField()
    content = models.TextField()
    added_on = models.DateTimeField(auto_now_add=True)
    objects = models.Manager()

    class Meta:
        verbose_name = 'Mpesa Call'
        verbose_name_plural = 'Mpesa Calls'


class MpesaCallBacks(models.Model):
    ip_address = models.TextField()
    caller = models.TextField()
    conversation_id = models.TextField()
    content = models.TextField()
    added_on = models.DateTimeField(auto_now_add=True)
    objects = models.Manager()

    class Meta:
        verbose_name = 'Mpesa Call Back'
        verbose_name_plural = 'Mpesa Call Backs'


class MpesaPayment(models.Model):
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    type = models.TextField()
    reference = models.TextField()
    first_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone_number = models.TextField()
    organization_balance = models.DecimalField(max_digits=10, decimal_places=2)
    added_on = models.DateTimeField(auto_now_add=True)
    objects = models.Manager()

    class Meta:
        verbose_name = 'Mpesa Payment'
        verbose_name_plural = 'Mpesa Payments'


class RicePrice(models.Model):
    id = models.AutoField(primary_key=True)
    paddy_rice = models.CharField(max_length=250)
    paddy_date = models.DateField()
    paddy_komboka = models.CharField(max_length=250)
    komboka_date = models.DateField()
    pishori = models.CharField(max_length=250)
    pishori_date = models.DateField()
    komboka= models.CharField(max_length=250)
    rice_date = models.DateField()
    objects = models.Manager()


class Region(models.Model):
    id = models.AutoField(primary_key=True)
    region = models.CharField(max_length=250)
    added_on = models.DateTimeField(auto_now_add=True)
    objects = models.Manager()


class Invoice(models.Model):
    id = models.AutoField(primary_key=True)
    customer_id = models.ForeignKey(Customer, on_delete=models.CASCADE)
    added_on = models.DateTimeField(auto_now_add=True)
    objects = models.Manager()


class InvoiceDetails(models.Model):
    id = models.AutoField(primary_key=True)
    invoice_id = models.ForeignKey(Invoice, on_delete=models.CASCADE)
    orders_id = models.ForeignKey(Orders, on_delete=models.CASCADE)
    added_on = models.DateTimeField(auto_now_add=True)
    objects = models.Manager()


class Tickets(models.Model):
    choices = ((1, "Pishori"), (2, "Komboka"))

    id = models.AutoField(primary_key=True)
    orders_id = models.CharField(max_length=255)
    customer_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=255)
    rice_type = models.CharField(choices=choices, max_length=255)
    kgs = models.CharField(max_length=255)
    farmer_id = models.ForeignKey(Farmer, on_delete=models.CASCADE)
    comment = models.TextField()
    status = models.BooleanField(default=False)
    added_on = models.DateTimeField(auto_now_add=True)
    objects = models.Manager()


class FarmerStock(models.Model):
    choices = ((1, "Pishori"), (2, "Komboka"))

    id = models.AutoField(primary_key=True)
    farmer_id = models.ForeignKey(Farmer, on_delete=models.CASCADE)
    rice_type = models.CharField(choices=choices, max_length=255)
    in_stock = models.CharField(max_length=255)
    added_on = models.DateField(auto_now_add=True)
    objects = models.Manager()
