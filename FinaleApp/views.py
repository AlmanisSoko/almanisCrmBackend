from django.shortcuts import render
from datetime import datetime, timedelta


from rest_framework import viewsets, generics
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication

from FinaleApp.models import Farmer, Orders, Customer, BillDetails, Payments, Bill
from FinaleApp.serializers import FarmerSerializer, OrdersSerializer, CustomerSerializer, BillSerializer, \
    PaymentsSerializer, BillDetailsSerializer, CustomerBillSerializer


# Create your views here.


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
        orders_details = Orders.objects.filter(farmer_id=serializer_data["id"])
        orders_details_serializers = OrdersSerializer(orders_details, many=True)
        serializer_data["orders"] = orders_details_serializers.data

        return Response({"error": False, "message": "Single Data Fetch", "data": serializer_data})

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


class CustomerViewSet(viewsets.ViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def list(self, request):
        customer = Customer.objects.all()
        serializer = CustomerSerializer(customer, many=True, context={"request": request})
        response_dict = {"error": False, "message": "All Customers List Data", "data": serializer.data}
        return Response(response_dict)

    def create(self, request):
        try:
            serializer = CustomerSerializer(data=request.data, context={"request": request})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            dict_response = {"error": False, "message": "Customer Data Stored Successfully"}
        except:
            dict_response = {"error": True, "message": "An Error Occurred"}

        return Response(dict_response)

    def retrieve(self, request, pk=None):
        queryset = Customer.objects.all()
        customer = get_object_or_404(queryset, pk=pk)
        serializer = CustomerSerializer(customer, context={"request": request})

        serializer_data = serializer.data
        # Accessing All the Orders Details of Current Customer
        orders_details = Orders.objects.filter(customer_id=serializer_data["id"])
        orders_details_serializers = OrdersSerializer(orders_details, many=True)
        serializer_data["orders"] = orders_details_serializers.data

        serializer_data1 = serializer.data
        # Accessing All the Payment Details of Current Customer
        payments_details = Payments.objects.filter(customer_id=serializer_data1["id"])
        payments_details_serializers = PaymentsSerializer(payments_details, many=True)
        serializer_data["payments"] = payments_details_serializers.data

        return Response({"error": False, "message": "Single Data Fetch", "data": serializer_data})

    def update(self, request, pk=None):
        try:
            queryset = Customer.objects.all()
            customer = get_object_or_404(queryset, pk=pk)
            serializer = CustomerSerializer(customer, data=request.data, context={"request": request})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            dict_response = {"error": False, "message": "Customer Data Updated Successfully"}
        except:
            dict_response = {"error": True, "message": "An Error Occurred"}

        return Response(dict_response)


class OrdersViewSet(viewsets.ViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def list(self, request):
        orders = Orders.objects.all()
        serializer = OrdersSerializer(orders, many=True, context={"request": request})
        response_dict = {"error": False, "message": "All Orders List Data", "data": serializer.data}
        return Response(response_dict)

    def create(self, request):
        try:
            serializer = OrdersSerializer(data=request.data, context={"request": request})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            dict_response = {"error": False, "message": "Order Stored Successfully"}
        except:
            dict_response = {"error": True, "message": "An Error Occurred"}

        return Response(dict_response)

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


class CustomerNameViewSet(generics.ListAPIView):
    serializer_class = CustomerSerializer

    def get_queryset(self):
        phone = self.kwargs["phone"]
        return Customer.objects.filter(phone=phone)


class CustomerDetailViewSet(generics.ListAPIView):
    serializer_class = CustomerSerializer

    def get_queryset(self):
        name = self.kwargs["name"]
        return Customer.objects.filter(name=name)


class FarmerNameViewSet(generics.ListAPIView):
    serializer_class = FarmerSerializer

    def get_queryset(self):
        name = self.kwargs["name"]
        return Farmer.objects.filter(name__contains=name)


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
        payments = Payments.objects.all()
        serializer = PaymentsSerializer(payments, many=True, context={"request": request})
        response_dict = {"error": False, "message": "All Payments List Data", "data": serializer.data}
        return Response(response_dict)

    def create(self, request):
        try:
            serializer = PaymentsSerializer(data=request.data, context={"request": request})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            dict_response = {"error": False, "message": "Payment Stored Successfully"}
        except:
            dict_response = {"error": True, "message": "An Error Occurred"}

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
            dict_response = {"error": False, "message": "Payment Updated Successfully"}
        except:
            dict_response = {"error": True, "message": "An Error Occurred"}

        return Response(dict_response)


class FarmerOnlyViewSet(generics.ListAPIView):
    serializer_class = FarmerSerializer

    def get_queryset(self):
        return Farmer.objects.all()


class GenerateBillViewSet(viewsets.ViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def create(self, request):
        #First Save Customer Data
        serializer = CustomerBillSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        serializer.save()

        customerBill_id = serializer.data['id']

        #Save Bill Data
        billdata={}
        billdata["customerbill_id"] = customerBill_id

        serializer2 = BillSerializer(data=billdata, context={"request": request})
        serializer2.is_valid()
        serializer2.save()
        bill_id = serializer2.data['id']

        # Adding and Saving Id into Orders Table
        orders_list = []
        for orders in request.data["order_details"]:
            print(orders)
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
        orders = Orders.objects.all()
        orders_serializer = OrdersSerializer(orders, many=True, context={"request": request})

        bill_count = Bill.objects.all()
        bill_count_serializer = BillSerializer(bill_count, many=True, context={"request": request})

        customer = Customer.objects.all()
        customer_serializer = CustomerSerializer(customer, many=True, context={"request": request})

        farmer = Farmer.objects.all()
        farmer_serializer = FarmerSerializer(farmer, many=True, context={"request": request})

        bill_details = BillDetails.objects.all()
        profit_amt = 0
        sell_amt = 0
        amount = 0
        for bill in bill_details:
            amount = amount + float(bill.order_id.amount)
            sell_amt = sell_amt + float(bill.order_id.amount)

        profit_amt = sell_amt - amount

        orders_pending = Orders.objects.filter(status=False)
        orders_pending_serializer = OrdersSerializer(orders_pending, many=True, context={"request": request})

        orders_complete = Orders.objects.filter(status=True)
        orders_complete_serializer = OrdersSerializer(orders_complete, many=True, context={"request": request})

        current_date = datetime.today().strftime("%Y-%m-%d")
        current_date1 = datetime.today()
        current_date_7days = current_date1 + timedelta(days=7)
        current_date_7days = current_date_7days.strftime("%Y-%m-%d")
        bill_details_today = BillDetails.objects.filter(added_on__date=current_date)
        profit_amt_today = 0
        sell_amt_today = 0
        amount_today = 0
        for bill in bill_details_today:
            amount_today = float(amount_today + float(bill.order_id.amount)) #* int(bill.qty)
            sell_amt_today = float(sell_amt_today + float(bill.order_id.amount)) #* int(bill.qty)

        profit_amt_today = sell_amt_today - amount_today

        bill_dates = BillDetails.objects.order_by().values("added_on__date").distinct()
        profit_chart_list = []
        sell_chart_list = []
        buy_chart_list = []
        for billdate in bill_dates:
            access_date = billdate["added_on__date"]

            bill_data = BillDetails.objects.filter(added_on__date=access_date)
            profit_amt_inner = 0
            sell_amt_inner = 0
            amount_inner = 0

            for billsingle in bill_data:
                amount_inner = float(amount_inner + float(billsingle.order_id.amount)) #* int(billsingle.order_id)
                sell_amt_inner = float(sell_amt_inner + float(billsingle.order_id.amount)) #* int(billsingle.order_id)

            profit_amt_inner = sell_amt_inner - amount_inner

            profit_chart_list.append({"date": access_date, "amt": profit_amt_inner})
            sell_chart_list.append({"date": access_date, "amt": sell_amt_inner})
            buy_chart_list.append({"date": access_date, "amt": amount_inner})

        dict_response = {"error": False, "message": "Home page data", "profit_amt_today": profit_amt_today, "sell_amt_today": sell_amt_today, "orders": len(orders_serializer.data),  "orders_complete": len(orders_complete_serializer.data), "orders_pending": len(orders_pending_serializer.data), "bill_count": len(bill_count_serializer.data), "customer": len(customer_serializer.data), "farmer": len(farmer_serializer.data), "sale_total": sell_amt, "buy_total": amount, "profit_total": profit_amt, "sell_chart": sell_chart_list, "buy_chart": buy_chart_list, "profit_chart": profit_chart_list}
        return Response(dict_response)


farmer_list = FarmerViewSet.as_view({"get": "list"})
farmer_create = FarmerViewSet.as_view({"post": "create"})
farmer_update = FarmerViewSet.as_view({"put": "update"})
