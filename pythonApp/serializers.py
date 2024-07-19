from djoser.serializers import UserCreateSerializer, UserSerializer
from django.contrib.auth import get_user_model
from rest_framework import serializers
from django.utils import timezone
from django.utils.timezone import make_aware

User = get_user_model()

from pythonApp.models import Farmer, Customer, Payments, Bill, Orders, BillDetails, CustomerBill, RicePrice, Region, \
    Invoice, InvoiceDetails, Tickets, FarmerStock


class UserCreateSerializer(UserCreateSerializer):
    user_type = serializers.CharField(default='normal', required=False)  # Add user_type field with default value

    class Meta(UserCreateSerializer.Meta):
        model = User
        fields = '__all__'  # Include user_type in fields

    def validate(self, attrs):
        attrs = super().validate(attrs)

        user_type = attrs.get('user_type')
        if user_type not in ['normal', 'admin']:  # Make sure user_type is either 'normal' or 'admin'
            raise serializers.ValidationError("Invalid user type")

        return attrs


class CustomUserSerializer(UserSerializer):
    last_login = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)

    class Meta(UserSerializer.Meta):
        fields = ('id', 'email', 'first_name', 'last_name', 'phone', 'last_login')

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        last_login = representation.get('last_login')

        if last_login:
            if isinstance(last_login, str):
                # If last_login is a string, try to parse it into a datetime object
                last_login = timezone.make_aware(timezone.datetime.fromisoformat(last_login))

            if not timezone.is_aware(last_login):
                # If it's still not aware, assume it's in the default timezone
                last_login = make_aware(last_login, timezone.get_current_timezone())

            formatted_last_login = timezone.localtime(last_login).strftime('%Y-%m-%d %H:%M:%S')
            representation['last_login'] = formatted_last_login

        return representation


class UserAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'

    def update(self, instance, validated_data):
        # Allow admins to update name and phone without email uniqueness check
        if self.context['request'].user.is_staff:
            instance.first_name = validated_data.get('first_name', instance.first_name)
            instance.last_name = validated_data.get('last_name', instance.last_name)
            instance.phone = validated_data.get('phone', instance.phone)
        else:
            # For regular users, update all fields
            instance.first_name = validated_data.get('first_name', instance.first_name)
            instance.last_name = validated_data.get('last_name', instance.last_name)
            instance.email = validated_data.get('email', instance.email)
            instance.phone = validated_data.get('phone', instance.phone)

        instance.save()
        return instance


class FarmerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Farmer
        fields = "__all__"


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = "__all__"


class BillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bill
        fields = "__all__"

    def to_representation(self, instance):
        response = super().to_representation(instance)
        response["customerbill"] = CustomerBillSerializer(instance.customerbill_id).data
        return response


class BillDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = BillDetails
        fields = "__all__"


class OrdersSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()

    class Meta:
        model = Orders
        fields = "__all__"

    def to_representation(self, instance):
        response = super().to_representation(instance)
        response["user"] = self.get_user(instance)  # Call the get_user method
        response["farmer"] = FarmerSerializer(instance.farmer_id).data
        response["customer"] = CustomerSerializer(instance.customer_id).data
        return response

    def get_user(self, instance):
        # Assuming 'username' is a field in your UserAccount model
        return instance.user_id.first_name


class OrderDateSerializer(serializers.Serializer):
    start_date = serializers.DateTimeField()
    end_date = serializers.DateTimeField()


class PaymentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payments
        fields = "__all__"

    def to_representation(self, instance):
        response = super().to_representation(instance)
        response["orders"] = OrdersSerializer(instance.orders_id).data
        response["customer"] = CustomerSerializer(instance.customer_id).data
        return response


class CustomerBillSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerBill
        fields = "__all__"


class RicePriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = RicePrice
        fields = "__all__"


class RegionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Region
        fields = "__all__"


class InvoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invoice
        fields = "__all__"

    def to_representation(self, instance):
        response = super().to_representation(instance)
        response["customer"] = CustomerSerializer(instance.customer_id).data
        return response


class InvoiceDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvoiceDetails
        fields = "__all__"

    def to_representation(self, instance):
        response = super().to_representation(instance)

        # Check if orders_id is not None before trying to serialize
        if instance.orders_id is not None:
            response["orders"] = OrdersSerializer(instance.orders_id).data
        else:
            response["orders"] = None

        return response



class InvoiceDetailedSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvoiceDetails
        fields = "__all__"

    def to_representation(self, instance):
        response = super().to_representation(instance)
        response["invoice"] = InvoiceSerializer(instance.invoice_id).data
        return response


class TicketsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tickets
        fields = "__all__"

    def to_representation(self, instance):
        response = super().to_representation(instance)
        response["farmer"] = FarmerSerializer(instance.farmer_id).data
        return response


class FarmerStockSerializer(serializers.ModelSerializer):
    class Meta:
        model = FarmerStock
        fields = "__all__"

    def to_representation(self, instance):
        response = super().to_representation(instance)
        response["farmer"] = FarmerSerializer(instance.farmer_id).data
        return response
