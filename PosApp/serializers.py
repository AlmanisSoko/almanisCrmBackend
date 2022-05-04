from rest_framework import serializers

# Create your serializers here
from PosApp.models import Farmer, Customer, Payments, Bill, Orders, BillDetails, CustomerBill


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
    class Meta:
        model = Orders
        fields = "__all__"

    def to_representation(self, instance):
        response = super().to_representation(instance)
        response["farmer"] = FarmerSerializer(instance.farmer_id).data
        response["customer"] = CustomerSerializer(instance.customer_id).data
        return response


class PaymentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payments
        fields = "__all__"

    def to_representation(self, instance):
        response = super().to_representation(instance)
        response["orders"] = OrdersSerializer(instance.orders_id).data
        return response

    def to_representation(self, instance):
        response = super().to_representation(instance)
        response["customer"] = CustomerSerializer(instance.customer_id).data
        return response


class CustomerBillSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerBill
        fields = "__all__"
