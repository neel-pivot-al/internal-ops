import base64
from datetime import datetime
from io import BytesIO

import pdfkit
from celery import shared_task
from django.contrib.staticfiles import finders
from django.db.models import F, Q, Sum, Value
from django.db.models.functions import Concat
from django.template.loader import render_to_string

from authentication.models import User
from internal_ops.celery import app
from project_management.models import Invoice, ProjectRate, WorkLog


@app.task
def generate_invoice_task(
    start_date: datetime, end_date: datetime, client_id: int
) -> None:
    worklogs = (
        WorkLog.objects.filter(
            billed_status=WorkLog.BillingStatus.UNBILLED,
            date_logged__range=(start_date, end_date),
            function__feature__project__client_id=client_id,
        )
        .order_by("function__feature__project__client")
        .prefetch_related(
            "function__feature__project",
            "developer",
        )
    )
    grand_total = 0
    invoice_items = []
    for worklog in worklogs:
        project = worklog.function.feature.project
        developer_rate = ProjectRate.objects.get(
            developer=worklog.developer,
            project=project,
        ).rate_per_hour
        total_cost = worklog.hours_worked * developer_rate
        grand_total += total_cost
        invoice_items.append(
            {
                "project_title": project.title,
                "description": worklog.function.description,
                "hours": worklog.hours_worked,
                "per_hour": developer_rate,
                "cost": total_cost,
            }
        )

    invoice = Invoice.objects.create(
        client_id=client_id,
        from_date=start_date,
        to_date=end_date,
        amount=0,
    )

    logo_path = finders.find("images/logo.png")
    if logo_path:
        with open(logo_path, "rb") as logo_file:
            image_base64 = base64.b64encode(logo_file.read()).decode("utf-8")
    else:
        image_base64 = ""

    cxt = {
        "logo_base64": image_base64,
        "grand_total": grand_total,
        "invoice_items": invoice_items,
    }

    html_string = render_to_string("invoices/invoice.html", cxt)
    options = {
        "page-size": "A4",
        "encoding": "UTF-8",
        "enable-local-file-access": "",
    }
    config = None

    pdf_bytes = pdfkit.from_string(
        html_string,
        options=options,
        configuration=config,
    )
    pdf_io = BytesIO(pdf_bytes)

    invoice.pdf_file.save(f"{invoice.id}.pdf", pdf_io)
    invoice.save()
