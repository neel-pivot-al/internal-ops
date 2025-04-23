import base64
import os
from datetime import datetime

import pdfkit
from django.conf import settings
from django.contrib.staticfiles import finders
from django.http import HttpResponse
from django.shortcuts import render
from django.template.loader import render_to_string
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from project_management.serializers import GenerateInvoiceSerializer
from project_management.tasks import generate_invoice_task


class InvoiceView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        invoice_id = "XMG34567"
        invoice = {
            "id": invoice_id,
            "date": datetime.now().strftime("%Y-%m-%d"),
            "customer_name": "John Doe",
            "items": [
                {
                    "project_title": "Project 1",
                    "developer_name": "Mark Twain",
                    "hours": 2,
                    "per_hour": 50,
                    "cost": 100,
                },
                {
                    "project_title": "Project 2",
                    "developer_name": "Jane Doe",
                    "hours": 3,
                    "per_hour": 35,
                    "cost": 105,
                },
            ],
        }
        invoice["grand_total"] = sum(item["cost"] for item in invoice["items"])

        static_path = os.path.join(settings.STATIC_URL, "images/logo.png")
        # generate complete url
        static_path = f"{request.build_absolute_uri(static_path)}"
        print(static_path)
        # Render HTML content using the template
        html_string = render_to_string(
            "invoices/invoice.html",
            {
                "invoice": invoice,
                "logo_base64": static_path,
            },
        )

        # Configure pdfkit options
        options = {
            "page-size": "A4",
            "encoding": "UTF-8",
        }

        # Path to wkhtmltopdf executable
        # If wkhtmltopdf is in PATH, you can omit configuration
        # Otherwise, specify the path like:
        # config = pdfkit.configuration(wkhtmltopdf='/usr/local/bin/wkhtmltopdf')
        config = None
        # Example for Windows:
        # config = pdfkit.configuration(wkhtmltopdf=r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe')

        # Generate PDF
        pdf = pdfkit.from_string(
            html_string, False, options=options, configuration=config
        )

        # Create HTTP response with PDF
        response = HttpResponse(pdf, content_type="application/pdf")
        response["Content-Disposition"] = (
            f'attachment; filename="invoice_{invoice_id}.pdf"'
        )

        return response


@api_view(["POST"])
def generate_invoice(request):
    cxt = {"request": request}
    serializer = GenerateInvoiceSerializer(data=request.data, context=cxt)
    serializer.is_valid(raise_exception=True)

    start_date = serializer.validated_data["start_date"]
    end_date = serializer.validated_data["end_date"]
    client = serializer.validated_data["client"]

    generate_invoice_task.delay(start_date, end_date, client.id)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


class FinanceView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({"message": "Hello, world!"})
