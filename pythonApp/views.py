from django.shortcuts import render, get_object_or_404
from djoser.views import UserViewSet
from datetime import datetime, timedelta

from django.db.models import Q, Sum, F, DecimalField, Subquery, OuterRef, FloatField

from rest_framework import viewsets, generics, status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from rest_framework_simplejwt.authentication import JWTAuthentication

from pythonApp import serializers

from pythonApp.models import Farmer, Orders, Customer, Payments, RicePrice, Region, Invoice, InvoiceDetails, Tickets, \
    FarmerStock, UserAccount
from pythonApp.serializers import FarmerSerializer, OrdersSerializer, CustomerSerializer, BillSerializer, \
    PaymentsSerializer, BillDetailsSerializer, CustomerBillSerializer, RicePriceSerializer, RegionSerializer, \
    InvoiceSerializer, InvoiceDetailsSerializer, TicketsSerializer, FarmerStockSerializer, UserAccountSerializer

from django.core.signing import TimestampSigner

from pythonProject import settings

User = get_user_model()

# Create your views here.


class SuperUserRegistrationView(UserViewSet):
    # Override get_permissions method to allow unauthenticated access only for create_superuser action
    def get_permissions(self):
        if self.action == "create_superuser":
            return [AllowAny()]
        return super().get_permissions()

    @action(["post"], detail=False, url_path="superuser")
    def create_superuser(self, request, *args, **kwargs):
        serializer = serializers.UserCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Create the user object using serializer.save()
        user = serializer.save(user_type='admin')  # Set the user_type to 'admin'

        if user:
            # Set user as a superuser and staff
            user.is_superuser = True
            user.is_staff = True
            user.is_active = True
            user.save()

            return Response({"error": False, "message": "Admin account created and activated successfully"}, status=status.HTTP_201_CREATED)
        else:
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserAccountUpdateView(generics.UpdateAPIView):
    serializer_class = UserAccountSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        user_id = self.kwargs.get('user_id')
        user = self.request.user

        if user_id:
            # If a user_id is provided, check if the user is an admin
            if user.is_staff:
                # Admin can edit name and phone of other users
                return get_object_or_404(User, id=user_id)

        # If no user_id or if the user is not an admin, allow users to update their own accounts
        return user

    def perform_update(self, serializer):
        user = self.request.user

        if user.is_staff:
            # Admins can update the name and phone without email uniqueness check
            serializer.save()
        else:
            # Regular users can update all fields, including email, with email uniqueness check
            email = serializer.validated_data.get('email')
            instance = serializer.instance

            if email and User.objects.exclude(pk=instance.pk).filter(email=email).exists():
                raise serializers.ValidationError("User with this email already exists.")

            serializer.save()


class UserAccountDeleteView(generics.DestroyAPIView):
    serializer_class = UserAccountSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]

    queryset = UserAccount.objects.all()  # Update with the correct queryset

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()

        # You can add additional logic here if needed

        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class FarmerViewSet(viewsets.ViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def list(self, request):
        farmer = Farmer.objects.all()
        serializer = FarmerSerializer(farmer, many=True, context={"request": request})

        response_dict = {"error": False, "message": "All Farmers List Data", "data": serializer.data}

        return Response(response_dict)

    def create(self, request):
        try:
            serializer = FarmerSerializer(data=request.data, context={"request": request})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            dict_response = {"error": False, "message": "Farmers Data Saved Successfully"}
        except:
            dict_response = {"error": True, "message": "Error During Saving Farmers Data"}

        return Response(dict_response)

    def retrieve(self, request, pk=None):
        queryset = Farmer.objects.all()
        farmer = get_object_or_404(queryset, pk=pk)
        serializer = FarmerSerializer(farmer, context={"request": request})

        serializer_data = serializer.data
        # Accessing All the Orders Details of Current Farmer
        orders_details = Orders.objects.filter(farmer_id=serializer_data["id"]).order_by('-id')
        orders_details_serializers = OrdersSerializer(orders_details, many=True)
        serializer_data["orders"] = orders_details_serializers.data

        # Accessing all kgs of current farmer
        kgs_total = Orders.objects.filter(farmer_id=serializer_data["id"])
        kgs = 0
        for total in kgs_total:
            kgs = kgs + float(total.kgs)

        # Accessing All Orders of Current Farmer
        orders_count = Orders.objects.filter(farmer_id=serializer_data["id"])
        orders_count_serializer = OrdersSerializer(orders_count, many=True, context={"request": request})

        # Accessing Rice Stock of Current Farmer
        stock_total = FarmerStock.objects.filter(farmer_id=serializer_data["id"])
        in_stock = 0
        for instock in stock_total:
            in_stock = in_stock + float(instock.in_stock)

        return Response({
            "error": False,
            "message": "Single Data Fetch",
            "kgs": kgs,
            "stock": in_stock,
            "orders_count": len(orders_count_serializer.data),
            "data": serializer_data})

    def update(self, request, pk=None):
        try:
            queryset = Farmer.objects.all()
            farmer = get_object_or_404(queryset, pk=pk)
            serializer = FarmerSerializer(farmer, data=request.data, context={"request": request})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            dict_response = {"error": False, "message": "Successfully Updated Farmer Data"}
        except:
            dict_response = {"error": True, "message": "Error During Updating Farmer Data"}

        return Response(dict_response)

    def destroy(self, request, pk=None):
        queryset = Farmer.objects.all()
        farmer = get_object_or_404(queryset, pk=pk)
        farmer.delete()
        return Response({"error": False, "message": "Farmer Deleted"})


class CustomerViewSet(viewsets.ViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    pagination_class = PageNumberPagination()

    def list(self, request):
        paginator = self.pagination_class
        customer = Customer.objects.all()
        page = paginator.paginate_queryset(customer, request, view=self)
        if page is not None:
            serializer = CustomerSerializer(page, many=True, context={"request": request})
            response_data = paginator.get_paginated_response(serializer.data).data
        else:
            serializer = CustomerSerializer(customer, many=True, context={"request": request})
            response_data = serializer.data

        response_dict = {"error": False, "message": "All Customers List Data", "data": response_data}
        return Response(response_dict)

    def create(self, request):
        try:
            serializer = CustomerSerializer(data=request.data, context={"request": request})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            dict_response = {"error": False, "message": "Customer Data Stored Successfully"}
        except:
            dict_response = {"error": True, "message": "Phone Number Exists In Database, Fill All Fields"}

        return Response(dict_response)

    def retrieve(self, request, pk=None):
        queryset = Customer.objects.all()
        customer = get_object_or_404(queryset, pk=pk)
        serializer = CustomerSerializer(customer, context={"request": request})

        serializer_data = serializer.data
        # Accessing All the Orders Details of Current Customer
        orders_details = Orders.objects.filter(customer_id=serializer_data["id"]).order_by('-id')
        orders_details_serializers = OrdersSerializer(orders_details, many=True)
        serializer_data["orders"] = orders_details_serializers.data

        # Accessing All Orders of Current Customer
        orders_count = Orders.objects.filter(customer_id=serializer_data["id"])
        orders_count_serializer = OrdersSerializer(orders_count, many=True, context={"request": request})

        # Total orders amount of current customer
        orders_total = Orders.objects.filter(customer_id=serializer_data["id"])
        amount = 0
        discount = 0
        kgs = 0
        for total in orders_total:
            amount = amount + float(total.amount)
            discount = discount + float(total.discount)
            kgs = kgs + float(total.kgs)

        serializer_data1 = serializer.data
        # Accessing All the Payment Details of Current Customer
        payments_details = Payments.objects.filter(customer_id=serializer_data1["id"]).order_by('-id')
        payments_details_serializers = PaymentsSerializer(payments_details, many=True)
        serializer_data["payments"] = payments_details_serializers.data

        serializer_data2 = serializer_data
        payment_count = Payments.objects.filter(customer_id=serializer_data2["id"])
        payment_count_serializer = PaymentsSerializer(payment_count, many=True, context={"request": request})

        # Total Payment of current customer
        payment_total = Payments.objects.filter(customer_id=serializer_data2["id"])
        t_amount = 0
        for balance in payment_total:
            t_amount = t_amount + float(balance.payment)

        balance = amount - t_amount

        dict_response = {"error": False, "message": "Single Data Fetch",
                         "data": serializer_data,
                         "payment": len(payment_count_serializer.data),
                         "buy_total": amount,
                         "payed_total": t_amount,
                         "balance": balance,
                         "kgs": kgs,
                         "discount": discount,
                         "orders_count": len(orders_count_serializer.data)}
        return Response(dict_response)

    def update(self, request, pk=None):
        try:
            queryset = Customer.objects.all()
            customer = get_object_or_404(queryset, pk=pk)
            serializer = CustomerSerializer(customer, data=request.data, context={"request": request})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            dict_response = {"error": False, "message": "Customer Data Updated Successfully"}

        except ValidationError as e:
            dict_response = {"error": True, "message": "Validation Error", "details": str(e)}
        except Exception as e:
            dict_response = {"error": True, "message": "An Error Occurred", "details": str(e)}

        return Response(dict_response,
                        status=status.HTTP_400_BAD_REQUEST if dict_response['error'] else status.HTTP_201_CREATED)

    def destroy(self, request, pk=None):
        queryset = Customer.objects.all()
        customer = get_object_or_404(queryset, pk=pk)
        # serializer = PaymentsSerializer(customer, context={"request": request})
        customer.delete()
        return Response({"error": False, "message": "Customer Deleted"})

    @action(detail=False, methods=['get'], url_path='customers-with-balance')
    def customers_with_balance(self, request):
        # Calculate the balance for each customer with a positive balance
        customers_with_balance = Customer.objects.annotate(
            total_orders=Subquery(
                Orders.objects.filter(customer_id=OuterRef('id'))
                .values('customer_id')
                .annotate(total=Sum(F('amount'), output_field=DecimalField(max_digits=10, decimal_places=2)))
                .values('total')
            ),
            total_payments=Subquery(
                Payments.objects.filter(customer_id=OuterRef('id'))
                .values('customer_id')
                .annotate(total=Sum('payment', output_field=DecimalField(max_digits=10, decimal_places=2))
                          )
                .values('total')
            )
        ).annotate(
            balance=F('total_orders') - F('total_payments')
        ).filter(balance__gt=0).order_by('id')

        # Serialize the data
        serializer = CustomerSerializer(customers_with_balance, many=True, context={"request": request})

        # Append the balance to each customer's data in the serialized response
        data_with_balance = serializer.data
        for customer_data, balance in zip(data_with_balance, customers_with_balance.values_list('balance', flat=True)):
            customer_data['balance'] = balance
        response_dict = {"error": False, "message": "Customers with Balance > 0", "data": data_with_balance}

        return Response(response_dict)

    @action(detail=False, methods=['get'], url_path='customers-with-excess')
    def customers_with_excess(self, request):
        # Calculate the balance for each customer with an excess balance
        customers_with_balance = Customer.objects.annotate(
            total_orders=Subquery(
                Orders.objects.filter(customer_id=OuterRef('id'))
                .values('customer_id')
                .annotate(total=Sum(F('amount'), output_field=DecimalField(max_digits=10, decimal_places=2)))
                .values('total')
            ),
            total_payments=Subquery(
                Payments.objects.filter(customer_id=OuterRef('id'))
                .values('customer_id')
                .annotate(total=Sum('payment', output_field=DecimalField(max_digits=10, decimal_places=2))
                          )
                .values('total')
            )
        ).annotate(
            balance=F('total_orders') - F('total_payments')
        ).filter(balance__lt=0).order_by('id')

        # Serialize the data
        serializer = CustomerSerializer(customers_with_balance, many=True, context={"request": request})

        # Append the balance to each customer's data in the serialized response
        data_with_balance = serializer.data
        for customer_data, balance in zip(data_with_balance, customers_with_balance.values_list('balance', flat=True)):
            customer_data['balance'] = balance
        response_dict = {"error": False, "message": "Customers with Balance < 0", "data": data_with_balance}

        return Response(response_dict)

    @action(detail=False, methods=['get'])
    def total_balance(self, request):
        # Calculate the total balance of all customers with a positive balance
        customers_with_balance = Customer.objects.annotate(
            total_orders=Subquery(
                Orders.objects.filter(customer_id=OuterRef('id'))
                .values('customer_id')
                .annotate(
                    total=Sum(F('amount'), output_field=DecimalField(max_digits=10, decimal_places=2))
                )
                .values('total')
            ),
            total_payments=Subquery(
                Payments.objects.filter(customer_id=OuterRef('id'))
                .values('customer_id')
                .annotate(total=Sum('payment', output_field=DecimalField(max_digits=10, decimal_places=2))
                          )
                .values('total')
            )
        ).annotate(
            balance=F('total_orders') - F('total_payments')
        ).filter(balance__gt=0).order_by('id')

        total_balance = customers_with_balance.aggregate(total_balance=Sum('balance'))['total_balance']

        return Response({"total_balance": total_balance})


class TotalBalanceView(APIView):
    def get(self, request):
        # Calculate the total orders and payments for all customers
        total_orders = Orders.objects.aggregate(total=Sum('amount'))['total'] or 0
        total_payments = Payments.objects.aggregate(total=Sum('payment'))['total'] or 0

        # Calculate the total balance for the entire app
        total_balance = total_orders - total_payments

        return Response({
            'total_balance': total_balance,
        }, status=status.HTTP_200_OK)


class TotalPaymentView(APIView):
    def get(self, request):
        # Calculate the total orders and payments for all customers
        total_payments = Payments.objects.aggregate(total=Sum('payment'))['total'] or 0

        return Response({
            'total_payments': total_payments,
        }, status=status.HTTP_200_OK)


class TotalDiscountView(APIView):
    def get(self, request):
        # Calculate the total orders and payments for all customers
        total_discount = Orders.objects.aggregate(total=Sum('discount'))['total'] or 0

        return Response({
            'total_discount': total_discount,
        }, status=status.HTTP_200_OK)


class TotalKilosView(APIView):
    def get(self, request):
        # Calculate the total orders and payments for all customers
        total_kgs = Orders.objects.aggregate(total=Sum('kgs'))['total'] or 0

        return Response({
            'total_kgs': total_kgs,
        }, status=status.HTTP_200_OK)


class CustomersWithPositiveBalanceViewSet(viewsets.ViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def list(self, request):
        # Calculate the balance for each customer
        customers_with_balance = Customer.objects.annotate(
            total_orders=Subquery(
                Orders.objects.filter(customer_id=OuterRef('id'))
                .values('customer_id')
                .annotate(
                    total=Sum(F('amount'), output_field=DecimalField(max_digits=10, decimal_places=2)))
                .values('total')
            ),
            total_payments=Subquery(
                Payments.objects.filter(customer_id=OuterRef('id'))
                .values('customer_id')
                .annotate(total=Sum('payment', output_field=DecimalField(max_digits=10, decimal_places=2)))
                .values('total')
            )
        ).annotate(
            balance=F('total_orders') - F('total_payments')
        ).filter(balance__gt=0).order_by('id')

        # Serialize the data
        serializer = CustomerSerializer(customers_with_balance, many=True, context={"request": request})

        # Append the balance to each customer's data in the serialized response
        data_with_balance = serializer.data
        for customer_data, balance in zip(data_with_balance, customers_with_balance.values_list('balance', flat=True)):
            customer_data['balance'] = balance
        response_dict = {"error": False, "message": "All Debtors List Data", "data": data_with_balance}

        return Response(response_dict)


class CustomersWithNegativeBalanceViewSet(viewsets.ViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def list(self, request):
        # Calculate the balance for each customer
        customers_with_balance = Customer.objects.annotate(
            total_orders=Subquery(
                Orders.objects.filter(customer_id=OuterRef('id'))
                .values('customer_id')
                .annotate(
                    total=Sum(F('amount'), output_field=DecimalField(max_digits=10, decimal_places=2)))
                .values('total')
            ),
            total_payments=Subquery(
                Payments.objects.filter(customer_id=OuterRef('id'))
                .values('customer_id')
                .annotate(total=Sum('payment', output_field=DecimalField(max_digits=10, decimal_places=2)))
                .values('total')
            )
        ).annotate(
            balance=F('total_orders') - F('total_payments')
        ).filter(balance__lt=0).order_by('id')

        # Serialize the data
        serializer = CustomerSerializer(customers_with_balance, many=True, context={"request": request})

        # Append the balance to each customer's data in the serialized response
        data_with_balance = serializer.data
        for customer_data, balance in zip(data_with_balance, customers_with_balance.values_list('balance', flat=True)):
            customer_data['balance'] = balance
        response_dict = {"error": False, "message": "Overpayment List Data", "data": data_with_balance}

        return Response(response_dict)


class TotalPositiveBalanceView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Calculate the total positive balance
        total_balance = Customer.objects.annotate(
            total_orders=Subquery(
                Orders.objects.filter(customer_id=OuterRef('id'))
                .values('customer_id')
                .annotate(
                    total=Sum(F('amount'), output_field=DecimalField(max_digits=10, decimal_places=2)))
                .values('total')
            ),
            total_payments=Subquery(
                Payments.objects.filter(customer_id=OuterRef('id'))
                .values('customer_id')
                .annotate(total=Sum('payment', output_field=DecimalField(max_digits=10, decimal_places=2)))
                .values('total')
            )
        ).annotate(
            balance=F('total_orders') - F('total_payments')
        ).filter(balance__gt=0).aggregate(total_positive_balance=Sum('balance'))

        # Rest of the code for additional data can be added here
        # Example: Calculate profit, count orders, and other statistics

        # Serialize the data and create a response dictionary
        response_data = {
            "total_positive_balance": total_balance['total_positive_balance'],
            # Add more data here as needed
        }

        return Response(response_data, status=status.HTTP_200_OK)


class TotalNegativeBalanceView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Calculate the total positive balance
        total_balance = Customer.objects.annotate(
            total_orders=Subquery(
                Orders.objects.filter(customer_id=OuterRef('id'))
                .values('customer_id')
                .annotate(
                    total=Sum(F('amount'), output_field=DecimalField(max_digits=10, decimal_places=2)))
                .values('total')
            ),
            total_payments=Subquery(
                Payments.objects.filter(customer_id=OuterRef('id'))
                .values('customer_id')
                .annotate(total=Sum('payment', output_field=DecimalField(max_digits=10, decimal_places=2)))
                .values('total')
            )
        ).annotate(
            balance=F('total_orders') - F('total_payments')
        ).filter(balance__lt=0).aggregate(total_negative_balance=Sum('balance'))

        return Response({"total_negative_balance": total_balance['total_negative_balance']}, status=status.HTTP_200_OK)


class OrdersViewSet(viewsets.ViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    pagination_class = PageNumberPagination()

    def list(self, request):
        paginator = self.pagination_class
        orders_query = Orders.objects.all().order_by('-id')
        page = paginator.paginate_queryset(orders_query, request, view=self)
        if page is not None:
            serializer = OrdersSerializer(page, many=True, context={"request": request})
            response_data = paginator.get_paginated_response(serializer.data).data
        else:
            serializer = OrdersSerializer(orders_query, many=True, context={"request": request})
            response_data = serializer.data

        today_date = datetime.today().strftime("%Y-%m-%d")
        daily_kgs = Orders.objects.filter(added_on__date=today_date).aggregate(total_kgs=Sum('kgs'))['total_kgs'] or 0

        response_dict = {
            "error": False,
            "message": "All Orders List Data",
            "daily_kgs": daily_kgs,
            "data": response_data
        }
        return Response(response_dict)

    def create(self, request):
        try:
            serializer = OrdersSerializer(data=request.data, context={"request": request})
            serializer.is_valid(raise_exception=True)
            serializer.save(user_id=self.request.user)

            dict_response = {"error": False, "message": "Order Stored Successfully"}

        except ValidationError as e:
            dict_response = {"error": True, "message": "Validation Error", "details": str(e)}
        except Exception as e:
            dict_response = {"error": True, "message": "An Error Occurred", "details": str(e)}

        return Response(dict_response,
                        status=status.HTTP_400_BAD_REQUEST if dict_response['error'] else status.HTTP_201_CREATED)

    def retrieve(self, request, pk=None):
        queryset = Orders.objects.all()
        orders = get_object_or_404(queryset, pk=pk)
        serializer = OrdersSerializer(orders, context={"request": request})
        return Response({"error": False, "message": "Single Data Fetch", "data": serializer.data})

    def update(self, request, pk=None):
        try:
            queryset = Orders.objects.all()
            orders = get_object_or_404(queryset, pk=pk)
            serializer = OrdersSerializer(orders, data=request.data, context={"request": request})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            dict_response = {"error": False, "message": "Order Updated Successfully"}
        except:
            dict_response = {"error": True, "message": "An Error Occurred"}

        return Response(dict_response)

    def destroy(self, request, pk=None):
        queryset = Orders.objects.all()
        orders = get_object_or_404(queryset, pk=pk)
        orders.delete()
        return Response({"error": False, "message": "Order Removed"})


class CustomerNameViewSet(generics.ListAPIView):
    serializer_class = CustomerSerializer

    def get_queryset(self):
        phone = self.kwargs["phone"]
        return Customer.objects.filter(Q(phone__contains=phone) | Q(secondary_phone__contains=phone))


class CustomerDetailViewSet(generics.ListAPIView):
    serializer_class = CustomerSerializer

    def get_queryset(self):
        name = self.kwargs["name"]
        return Customer.objects.filter(name__contains=name)


class FarmerNameViewSet(generics.ListAPIView):
    serializer_class = FarmerSerializer

    def get_queryset(self):
        name = self.kwargs["name"]
        return Farmer.objects.filter(name__contains=name)


class FarmerStockNameViewSet(generics.ListAPIView):
    serializer_class = FarmerStockSerializer

    def get_queryset(self):
        name = self.kwargs["name"]
        return FarmerStock.objects.filter(farmer_id__name__contains=name)


class OrderNameViewSet(generics.ListAPIView):
    serializer_class = OrdersSerializer

    def get_queryset(self):
        customer_name = self.kwargs["customer_name"]
        return Orders.objects.filter(customer_name__contains=customer_name)


class OrderByNameViewSet(generics.ListAPIView):
    serializer_class = OrdersSerializer

    def get_queryset(self):
        id = self.kwargs["id"]
        return Orders.objects.filter(id__contains=id)


class CustomerOnlyViewSet(generics.ListAPIView):
    serializer_class = CustomerSerializer

    def get_queryset(self):
        return Customer.objects.all()


class PaymentsViewSet(viewsets.ViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def list(self, request):
        payments = Payments.objects.all().order_by('-id')
        serializer = PaymentsSerializer(payments, many=True, context={"request": request})
        response_dict = {"error": False, "message": "All Payments List Data", "data": serializer.data}
        return Response(response_dict)

    def create(self, request):
        try:
            order_id = request.data.get("orders_id")
            payment_amount = float(request.data.get("payment"))

            # Get the order details
            order = Orders.objects.get(id=order_id)
            order_amount = float(order.amount)

            # Calculate total payments made for the order
            total_payments = Payments.objects.filter(orders_id=order_id).aggregate(Sum("payment"))["payment__sum"]
            total_payments = total_payments if total_payments else 0.0

            # Calculate remaining balance
            remaining_balance = order_amount - total_payments

            if payment_amount <= remaining_balance:
                serializer = PaymentsSerializer(data=request.data, context={"request": request})
                serializer.is_valid(raise_exception=True)
                serializer.save()

                dict_response = {
                    "error": False,
                    "message": "Payment Stored Successfully",
                    "remaining_balance": remaining_balance
                }
            else:
                dict_response = {
                    "error": True,
                    "message": "Payment amount exceeds remaining balance",
                    "remaining_balance": remaining_balance
                }
        except Exception as e:
            dict_response = {"error": True, "message": "An Error Occurred", "remaining_balance": remaining_balance}

        print("Payment Creation Debug Info:")
        print(f"Order Amount: {order_amount}")
        print(f"Total Payments: {total_payments}")
        print(f"Remaining Balance: {remaining_balance}")
        print(f"Payment Amount: {payment_amount}")
        print(dict_response)

        return Response(dict_response)

    def retrieve(self, request, pk=None):
        queryset = Payments.objects.all()
        payments = get_object_or_404(queryset, pk=pk)
        serializer = PaymentsSerializer(payments, context={"request": request})
        return Response({"error": False, "message": "Single Data Fetch", "data": serializer.data})

    def update(self, request, pk=None):
        try:
            queryset = Payments.objects.all()
            payments = get_object_or_404(queryset, pk=pk)
            serializer = PaymentsSerializer(payments, data=request.data, context={"request": request})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            dict_response = {"error": False, "message": "Payment Re-Processed Successfully"}
        except:
            dict_response = {"error": True, "message": "An Error Occurred"}

        return Response(dict_response)

    def destroy(self, request, pk=None):
        queryset = Payments.objects.all()
        payments = get_object_or_404(queryset, pk=pk)
        payments.delete()
        return Response({"error": False, "message": "Payment Removed"})


class FarmerOnlyViewSet(generics.ListAPIView):
    serializer_class = FarmerSerializer

    def get_queryset(self):
        return Farmer.objects.all()


class FarmerOnlyNameViewSet(generics.ListAPIView):
    serializer_class = FarmerSerializer

    def get_queryset(self):
        queryset = Farmer.objects.filter(id__in=FarmerStock.objects.values_list('farmer_id', flat=True))
        return queryset


class GenerateBillViewSet(viewsets.ViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def create(self, request):
        # First Save Customer Data
        serializer = CustomerBillSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        serializer.save()

        customerBill_id = serializer.data['id']

        # Save Bill Data
        billdata = {}
        billdata["customerbill_id"] = customerBill_id

        serializer2 = BillSerializer(data=billdata, context={"request": request})
        serializer2.is_valid()
        serializer2.save()
        bill_id = serializer2.data['id']

        # Adding and Saving Id into Orders Table
        orders_list = []
        for orders in request.data["order_details"]:
            orders1 = {}
            orders1["order_id"] = orders["id"]
            orders1["bill_id"] = bill_id

            orders_list.append(orders1)

        serializer3 = BillDetailsSerializer(data=orders_list, many=True,
                                            context={"request": request})
        serializer3.is_valid()
        serializer3.save()

        dict_response = {"error": False, "message": "Bill Generate Successfully"}
        return Response(dict_response)


class HomeApiViewSet(viewsets.ViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def list(self, request):
        customer = Customer.objects.all()
        customer_serializer = CustomerSerializer(customer, many=True, context={"request": request})

        farmer = Farmer.objects.all()
        farmer_serializer = FarmerSerializer(farmer, many=True, context={"request": request})

        others_transport = Orders.objects.filter(transporters=1)
        others_transport_serializer = OrdersSerializer(others_transport, many=True, context={"request": request})

        inhouse_transport = Orders.objects.filter(transporters=2)
        inhouse_transport_serializer = OrdersSerializer(inhouse_transport, many=True, context={"request": request})

        # get daily data
        current_date = datetime.today().strftime("%Y-%m-%d")
        current_date1 = datetime.today()
        current_date_7days = current_date1 + timedelta(days=7)
        current_date_7days = current_date_7days.strftime("%Y-%m-%d")
        bill_details_today = Orders.objects.filter(added_on__date=current_date)
        transport_today = 0
        rider_today = 0
        packaging_today = 0
        for bill in bill_details_today:
            transport_today += float(bill.transport)
            rider_today += float(bill.rider)
            packaging_today += float(bill.packaging)

        dict_response = {
                         "error": False,
                         "message": "Home page data",
                         "others_transport": len(others_transport_serializer.data),
                         "inhouse_transport": len(inhouse_transport_serializer.data),
                         "customer": len(customer_serializer.data),
                         "farmer": len(farmer_serializer.data),
                         "packaging_today": packaging_today,
                         "transport_today": transport_today,
                         "rider_today": rider_today,
                         }
        return Response(dict_response)


class DashboardView(viewsets.ViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def list(self, request):
        total_sales = Orders.objects.all()
        amount = 0
        net_sales = 0
        for sales in total_sales:
            amount += float(
                float(sales.price) * float(sales.kgs) + float(sales.transport) + float(
                    sales.packaging) + float(sales.rider))
            net_sales += float(
                float(sales.price) * float(sales.kgs) + float(sales.transport) + float(
                    sales.packaging) + float(sales.rider) - float(sales.discount))

        bill_details = Orders.objects.all()
        packaging = 0
        transport = 0
        rider = 0
        rice = 0
        profit = 0
        for bill in bill_details:
            packaging += float(bill.packaging)
            transport += float(bill.transport)
            rider += float(bill.rider)
            rice += float(float(bill.kgs) * float(bill.farmer_price))
            profit += float(float(float(bill.price) - float(bill.farmer_price)) * float(bill.kgs))

        overhead = packaging + transport + rider

        dict_response = {
            "error": False,
            "message": "Dashboard",
            "buy_total": amount,
            "transport": transport,
            "packaging": packaging,
            "rider": rider,
            "rice": rice,
            "profit": profit,
            "overhead": overhead,
        }

        return Response(dict_response)


class PaymentBreakdownView(viewsets.ViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def list(self, request):
        paid_mpesa = Payments.objects.filter(payment_mode=2)
        paid_mpesa_serializer = PaymentsSerializer(paid_mpesa, many=True, context={"request": request})

        paid_cash = Payments.objects.filter(payment_mode=1)
        paid_cash_serializer = PaymentsSerializer(paid_cash, many=True, context={"request": request})

        paid_bank = Payments.objects.filter(payment_mode=3)
        paid_bank_serializer = PaymentsSerializer(paid_bank, many=True, context={"request": request})

        paid_promo = Payments.objects.filter(payment_mode=5)
        paid_promo_serializer = PaymentsSerializer(paid_promo, many=True, context={"request": request})

        paid_trade = Payments.objects.filter(payment_mode=4)
        paid_trade_serializer = PaymentsSerializer(paid_trade, many=True, context={"request": request})

        paid_compensation = Payments.objects.filter(payment_mode=6)
        paid_compensation_serializer = PaymentsSerializer(paid_compensation, many=True, context={"request": request})

        paid_topup = Payments.objects.filter(payment_mode=7)
        paid_topup_serializer = PaymentsSerializer(paid_topup, many=True, context={"request": request})

        dict_reposne = {
            "error": False,
            "message": "Payments Breakdown",
            "paid_mpesa": len(paid_mpesa_serializer.data),
            "paid_cash": len(paid_cash_serializer.data),
            "paid_bank": len(paid_bank_serializer.data),
            "paid_trade": len(paid_trade_serializer.data),
            "paid_promo": len(paid_promo_serializer.data),
            "paid_compensation": len(paid_compensation_serializer.data),
            "paid_topup": len(paid_topup_serializer.data),
        }

        return Response(dict_reposne)


class CustomerRegionView(viewsets.ViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def list(self, request):
        nairobi = Customer.objects.filter(region=1)
        nairobi_serializer = CustomerSerializer(nairobi, many=True, context={"request": request})

        nyanza = Customer.objects.filter(region=2)
        nyanza_serializer = CustomerSerializer(nyanza, many=True, context={"request": request})

        central = Customer.objects.filter(region=3)
        central_serializer = CustomerSerializer(central, many=True, context={"request": request})

        coast = Customer.objects.filter(region=4)
        coast_serializer = CustomerSerializer(coast, many=True, context={"request": request})

        eastern = Customer.objects.filter(region=5)
        eastern_serializer = CustomerSerializer(eastern, many=True, context={"request": request})

        north_eastern = Customer.objects.filter(region=6)
        north_eastern_serializer = CustomerSerializer(north_eastern, many=True, context={"request": request})

        western = Customer.objects.filter(region=7)
        western_serializer = CustomerSerializer(western, many=True, context={"request": request})

        rift_valley = Customer.objects.filter(region=8)
        rift_valley_serializer = CustomerSerializer(rift_valley, many=True, context={"request": request})

        dict_response = {
            "error": False,
            "message": "Customers Per Region",
            "nairobi": len(nairobi_serializer.data),
            "central": len(central_serializer.data),
            "nyanza": len(nyanza_serializer.data),
            "eastern": len(eastern_serializer.data),
            "north_eastern": len(north_eastern_serializer.data),
            "coast": len(coast_serializer.data),
            "western": len(western_serializer.data),
            "rift_valley": len(rift_valley_serializer.data),
        }

        return Response(dict_response)


class DailyDataView(viewsets.ViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def list(self, request):
        bill_dates = Orders.objects.order_by().values("added_on__date").distinct()
        sell_chart_list = []
        profit_chart_list = []
        transport_chart_list = []
        packaging_chart_list = []
        kilos_chart_list = []
        buy_chart_list = []
        for billdate in bill_dates:
            access_date = billdate["added_on__date"]

            bill_data = Orders.objects.filter(added_on__date=access_date)
            sell_amt_inner = 0
            amount_inner = 0
            transport_amt_inner = 0
            packaging_amt_inner = 0
            kilos_amt_inner = 0

            for billsingle in bill_data:
                amount_inner += float(billsingle.amount)
                sell_amt_inner += float(billsingle.amount)
                transport_amt_inner += float(billsingle.transport)
                packaging_amt_inner += float(billsingle.packaging)
                kilos_amt_inner += float(billsingle.kgs)

            profit_chart_list.append({"date": access_date, "amt": sell_amt_inner})
            sell_chart_list.append({"date": access_date, "amt": sell_amt_inner})
            buy_chart_list.append({"date": access_date, "amt": amount_inner})
            packaging_chart_list.append({"date": access_date, "amt": packaging_amt_inner})
            transport_chart_list.append({"date": access_date, "amt": transport_amt_inner})
            kilos_chart_list.append({"date": access_date, "amt": kilos_amt_inner})

        dict_response = {
            "error": False,
            "message": "Daily Data",
            "sell_chart": sell_chart_list,
            "buy_chart": buy_chart_list,
            "transport_chart": transport_chart_list,
            "packaging_chart": packaging_chart_list,
            "kilos_chart": kilos_chart_list,
        }

        return Response(dict_response)


class MonthlyDataView(viewsets.ViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def list(self, request):
        # get monthly data
        from datetime import date
        month_dates = Orders.objects.order_by().values("added_on__month", "added_on__year").distinct()
        month_chart_list = []
        month_kilos_chart_list = []
        discount_month_chart_list = []
        profit_month_chart_list = []
        month_farmer_chart_list = []
        for month in month_dates:
            access_month = month["added_on__month"]
            access_year = month["added_on__year"]

            month_data = Orders.objects.filter(added_on__month=access_month, added_on__year=access_year)
            month_total = 0
            month_kilos = 0
            month_discount = 0
            month_profit = 0
            month_farmer = 0
            access_date = date(year=access_year, month=access_month, day=1)
            for month_single in month_data:
                month_total += float(
                    float(month_single.price) * float(month_single.kgs) + float(month_single.transport) + float(
                        month_single.packaging) + float(month_single.rider))
                month_kilos += float(month_single.kgs)
                month_profit += float(
                    float(float(month_single.price) - float(month_single.farmer_price)) * float(month_single.kgs))
                month_discount += float(month_single.discount)
                month_farmer += float(float(month_single.farmer_price) * float(month_single.kgs))

            month_chart_list.append({"date": access_date, "amt": month_total})
            month_kilos_chart_list.append({"date": access_date, "amt": month_kilos})
            discount_month_chart_list.append({"date": access_date, "amt": month_discount})
            profit_month_chart_list.append({"date": access_date, "amt": month_profit})
            month_farmer_chart_list.append({"date": access_date, "amt": month_farmer})

        dict_response = {
            "error": False,
            "message": "Monthly Data",

            "month_chart": month_chart_list,
            "month_profit": profit_month_chart_list,
            "month_discount": discount_month_chart_list,
            "month_farmer": month_farmer_chart_list,
            "month_kilos_chart": month_kilos_chart_list,
        }

        return Response(dict_response)


class YearlyDataView(viewsets.ViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def list(self, request):
        # get yearly data
        from datetime import date
        year_dates = Orders.objects.order_by().values("added_on__year").distinct()
        year_total_chart_list = []
        year_kilos_chart_list = []
        year_profit_chart_list = []
        year_farmer_chart_list = []
        year_discount_chart_list = []
        year_packaging_chart_list = []
        year_transport_chart_list = []
        year_rider_chart_list = []
        for year in year_dates:
            access_year = year["added_on__year"]

            year_data = Orders.objects.filter(added_on__year=access_year)
            year_total = 0
            year_profit = 0
            year_packaging = 0
            year_transport = 0
            year_rider = 0
            year_farmer = 0
            year_discount = 0
            year_kilos = 0
            access_year_date = date(year=access_year, month=1, day=1)
            for year_single in year_data:
                year_total += float(
                    float(year_single.price) * float(year_single.kgs) + float(year_single.transport) + float(
                        year_single.packaging) + float(year_single.rider))
                year_profit += float(
                    float(float(year_single.price) - float(year_single.farmer_price)) * float(
                        year_single.kgs))
                year_packaging += float(year_single.packaging)
                year_transport += float(year_single.transport)
                year_rider += float(year_single.rider)
                year_farmer += float(float(year_single.farmer_price) * float(year_single.kgs))
                year_discount += float(year_single.discount)
                year_kilos += float(year_single.kgs)

            year_total_chart_list.append({"date": access_year_date, "amt": year_total})
            year_profit_chart_list.append({"date": access_year_date, "amt": year_profit})
            year_packaging_chart_list.append({"date": access_year_date, "amt": year_packaging})
            year_transport_chart_list.append({"date": access_year_date, "amt": year_transport})
            year_rider_chart_list.append({"date": access_year_date, "amt": year_rider})
            year_farmer_chart_list.append({"date": access_year_date, "amt": year_farmer})
            year_discount_chart_list.append({"date": access_year_date, "amt": year_discount})
            year_kilos_chart_list.append({"date": access_year_date, "amt": year_kilos})

        dict_response = {
            "error": False,
            "message": "Yearly Data",
            "year_kilos": year_kilos_chart_list,
            "year_total": year_total_chart_list,
            "year_discount": year_discount_chart_list,
            "year_packaging_chart": year_packaging_chart_list,
            "year_transport_chart": year_transport_chart_list,
            "year_rider_chart": year_rider_chart_list,
            "year_farmer": year_farmer_chart_list,
            "year_profit": year_profit_chart_list,
        }

        return Response(dict_response)


class RicePriceViewSet(viewsets.ViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def list(self, request):
        rice = RicePrice.objects.all()
        serializer = RicePriceSerializer(rice, many=True, context={"request": request})
        response_dict = {"error": False, "message": "All Rice Price List Data", "data": serializer.data}
        return Response(response_dict)

    def create(self, request):
        try:
            serializer = RicePriceSerializer(data=request.data, context={"request": request})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            dict_response = {"error": False, "message": "Rice Price Stored Successfully"}
        except:
            dict_response = {"error": True, "message": "Check date format, Fill All Fields"}

        return Response(dict_response)


class RegionViewSet(viewsets.ViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def list(self, request):
        region = Region.objects.all()
        serializer = RegionSerializer(region, many=True, context={"request": request})
        response_dict = {"error": False, "message": "All Farmers List Data", "data": serializer.data}

        return Response(response_dict)

    def create(self, request):
        try:
            serializer = RegionSerializer(data=request.data, context={"request": request})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            dict_response = {"error": False, "message": "Order Stored Successfully"}
        except:
            dict_response = {"error": True, "message": "An Error Occurred"}

        return Response(dict_response)

    def retrieve(self, request, pk=None):
        queryset = Region.objects.all()
        region = get_object_or_404(queryset, pk=pk)
        serializer = RegionSerializer(region, context={"request": request})

        return Response({"error": False, "message": "Single Data Fetch", "data": serializer.data})

    def update(self, request, pk=None):
        try:
            queryset = Region.objects.all()
            region = get_object_or_404(queryset, pk=pk)
            serializer = RegionSerializer(region, data=request.data, context={"request": request})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            dict_response = {"error": False, "message": "Successfully Updated Farmer Data"}
        except:
            dict_response = {"error": True, "message": "Error During Updating Farmer Data"}

        return Response(dict_response)

    def destroy(self, request, pk=None):
        queryset = Region.objects.all()
        region = get_object_or_404(queryset, pk=pk)
        region.delete()
        return Response({"error": False, "message": "Farmer Deleted"})


class InvoiceViewSet(viewsets.ViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def list(self, request):
        invoice = Invoice.objects.all().order_by('-id')
        serializer = InvoiceSerializer(invoice, many=True, context={"request": request})

        # list invoice details
        invoice_data = serializer.data
        invoicelist = []

        for invoice in invoice_data:
            # access invoice details of current invoice id
            invoice_details = InvoiceDetails.objects.filter(invoice_id=invoice["id"])
            invoice_details_serializer = InvoiceDetailsSerializer(invoice_details, many=True)
            invoice["invoice_details"] = invoice_details_serializer.data
            invoicelist.append(invoice)

        response_dict = {"error": False, "message": "All Invoices List Data", "data": invoicelist}

        return Response(response_dict)

    def create(self, request):
        try:
            serializer = InvoiceSerializer(data=request.data, context={"request": request})
            serializer.is_valid(raise_exception=True)
            serializer.save()

            # access invoice id
            invoice_id = serializer.data["id"]

            # access saved serializer id
            invoice_details_list = []
            for invoice_detail in request.data["invoice_details"]:
                # add invoice id  for invoice detail serializer
                invoice_detail["invoice_id"] = invoice_id
                invoice_details_list.append(invoice_detail)

            # save invoice details to table
            serializer1 = InvoiceDetailsSerializer(data=invoice_details_list, many=True, context={"request": request})
            serializer1.is_valid()
            serializer1.save()

            dict_response = {"error": False, "message": "Invoice Stored Successfully"}
        except:
            dict_response = {"error": True, "message": "An Error Occurred"}

        return Response(dict_response)

    def retrieve(self, request, pk=None):
        queryset = Invoice.objects.all()
        invoice = get_object_or_404(queryset, pk=pk)
        serializer = InvoiceSerializer(invoice, context={"request": request})

        serializer_data = serializer.data
        # access invoice details of current invoice id
        invoice_details = InvoiceDetails.objects.filter(invoice_id=serializer_data["id"])
        invoice_details_serializer = InvoiceDetailsSerializer(invoice_details, many=True)
        serializer_data["invoice_details"] = invoice_details_serializer.data

        return Response({"error": False, "message": "Single Data Fetch", "data": serializer_data})

    def update(self, request, pk=None):
        try:
            queryset = Invoice.objects.all()
            invoice = get_object_or_404(queryset, pk=pk)
            serializer = InvoiceSerializer(invoice, data=request.data, context={"request": request})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            dict_response = {"error": False, "message": "Successfully Updated Invoice Data"}
        except:
            dict_response = {"error": True, "message": "Error During Updating Invoice Data"}

        return Response(dict_response)

    def destroy(self, request, pk=None):
        queryset = Invoice.objects.all()
        invoice = get_object_or_404(queryset, pk=pk)
        invoice.delete()
        return Response({"error": False, "message": "Invoice Deleted"})


class TicketViewSet(viewsets.ViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def list(self, request):
        tickets = Tickets.objects.all().order_by('-id')
        serializer = TicketsSerializer(tickets, many=True, context={"request": request})
        response_dict = {"error": False, "message": "Tickets List Data", "data": serializer.data}
        return Response(response_dict)

    def create(self, request):
        try:
            serializer = TicketsSerializer(data=request.data, context={"request": request})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            dict_response = {"error": False, "message": "Ticket created Successfully"}
        except:
            dict_response = {"error": True, "message": "An Error Occurred"}
        return Response(dict_response)

    def retrieve(self, request, pk=None):
        queryset = Tickets.objects.all()
        tickets = get_object_or_404(queryset, pk=pk)
        serializer = TicketsSerializer(tickets, context={"request": request})
        return Response({"error": False, "message": "Single Data Fetch", "data": serializer.data})

    def update(self, request, pk=None):
        try:
            queryset = Tickets.objects.all()
            tickets = get_object_or_404(queryset, pk=pk)
            serializer = TicketsSerializer(tickets, data=request.data, context={"request": request})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            dict_response = {"error": False, "message": "Successfully Updated Ticket Data"}
        except:
            dict_response = {"error": True, "message": "Error During Updating Ticket Data"}
        return Response(dict_response)

    def destroy(self, pk=None):
        queryset = Tickets.objects.all()
        tickets = get_object_or_404(queryset, pk=pk)
        tickets.delete()
        return Response({"error": False, "message": "Ticket Deleted"})

    @action(detail=True, methods=['post'])
    def save_comment(self, request, pk=None):
        try:
            queryset = Tickets.objects.all()
            ticket = get_object_or_404(queryset, pk=pk)
            comment = request.data.get('comment')
            ticket.comment = comment
            ticket.save()
            dict_response = {"error": False, "message": "Comment added successfully"}
        except:
            dict_response = {"error": True, "message": "An Error Occurred while adding the comment"}
        return Response(dict_response)


class FarmerStockViewSet(viewsets.ViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def list(self,request):
        stock = FarmerStock.objects.all().order_by('-id')
        serializer = FarmerStockSerializer(stock, many=True, context={"request": request})
        response_dict = {"error": False, "message": "All Farmer Stock", "data": serializer.data}
        return Response(response_dict)

    def create(self, request):
        try:
            serializer = FarmerStockSerializer(data=request.data, context={"request": request})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            dict_response = {"error": False, "message": "Stock Added Successfully"}
        except:
            dict_response = {"error": True, "message": "An Error Occurred"}
        return Response(dict_response)

    def retrieve(self, request, pk=None):
        queryset = FarmerStock.objects.all()
        stock = get_object_or_404(queryset, pk=pk)
        serializer = FarmerStockSerializer(stock, context={"request": request})
        return Response({"error": False, "message": "Single Data Fetch", "data": serializer.data})

    def update(self, request, pk=None):
        try:
            queryset = FarmerStock.objects.all()
            stock = get_object_or_404(queryset, pk=pk)
            serializer = FarmerStockSerializer(stock, data=request.data, context={"request": request})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            dict_response = {"error": False, "message": "Successfully Updated Stock Data"}
        except:
            dict_response = {"error": True, "message": "Error During Updating Stock Data"}
        return Response(dict_response)

    def destroy(self, pk=None):
        queryset = FarmerStock.objects.all()
        stock = get_object_or_404(queryset, pk=pk)
        stock.delete()
        return Response({"error": False, "message": "Stock Deleted"})


farmer_list = FarmerViewSet.as_view({"get": "list"})
farmer_create = FarmerViewSet.as_view({"post": "create"})
farmer_update = FarmerViewSet.as_view({"put": "update"})
farmer_destroy = FarmerViewSet.as_view({"delete": "destroy"})

