from django.contrib.auth import get_user_model
from django.db import models
from simple_history.models import HistoricalRecords

from core.models import BaseHistoryModel
from project_management.utils import get_developer_rate

User = get_user_model()


# Developer Profile
class DeveloperProfile(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="developer_profile"
    )
    skills = models.TextField()
    time_zone = models.CharField(max_length=100)
    availability = models.BooleanField(default=True)


# Project Model
class Project(models.Model):
    class Status(models.TextChoices):
        NEGOTIATING = "negotiating", "Negotiating"
        SECURED = "secured", "Secured"
        IN_PROGRESS = "in_progress", "In Progress"
        COMPLETED = "completed", "Completed"
        ON_HOLD = "on_hold", "On Hold"
        CANCELLED = "cancelled", "Cancelled"

    class Priority(models.IntegerChoices):
        P0 = 0, "P0"
        P1 = 1, "P1"
        P2 = 2, "P2"
        P3 = 3, "P3"

    title = models.CharField(max_length=200)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=Status.choices)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    priority = models.IntegerField(choices=Priority.choices, default=Priority.P3)
    client = models.ForeignKey(
        User,
        related_name="client_projects",
        limit_choices_to={"role": "client"},
        on_delete=models.CASCADE,
        null=True,
    )
    developers = models.ManyToManyField(
        User,
        related_name="developer_projects",
        limit_choices_to={"role": "developer"},
    )

    history = HistoricalRecords()

    def __str__(self):
        return self.title


class ProjectRate(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="rates")
    developer = models.ForeignKey(
        User, on_delete=models.CASCADE, limit_choices_to={"role": "developer"}
    )
    rate = models.DecimalField(max_digits=10, decimal_places=2)

    history = HistoricalRecords()

    class Meta:
        unique_together = ("project", "developer")


# Feature Model
class Feature(models.Model):
    class Status(models.TextChoices):
        BACKLOG = "backlog", "Backlog"
        SPECS = "specs", "Specs"
        IN_PROGRESS = "in_progress", "In Progress"
        COMPLETED = "completed", "Completed"
        BLOCKED = "blocked", "Blocked"

    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name="features"
    )
    title = models.CharField(max_length=200)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=Status.choices, default="backlog")

    history = HistoricalRecords()

    def calculate_cost(self):
        return (
            self.functions.aggregate(total_cost=models.Sum("cost"))["total_cost"] or 0
        )

    def calculate_estimated_time(self):
        return (
            self.functions.aggregate(total_time=models.Sum("estimated_time"))[
                "total_time"
            ]
            or 0
        )

    def __str__(self):
        return self.title


# Function Model
class Function(models.Model):
    class Status(models.TextChoices):
        BACKLOG = "backlog", "Backlog"
        SPECS = "specs", "Specs"
        IN_PROGRESS = "in_progress", "In Progress"
        COMPLETED = "completed", "Completed"
        BLOCKED = "blocked", "Blocked"

    feature = models.ForeignKey(
        Feature,
        on_delete=models.CASCADE,
        related_name="functions",
    )
    title = models.CharField(max_length=200)
    description = models.TextField()
    status = models.CharField(
        max_length=20,
        choices=Feature.Status.choices,
        default=Feature.Status.BACKLOG,
    )
    developer = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={"role": "developer"},
    )
    estimated_time = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True
    )
    cost = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True, editable=False
    )

    history = HistoricalRecords()

    def save(self, *args, **kwargs):
        developer_rate = get_developer_rate(
            project=self.project,
            developer=self.developer,
        )
        self.cost = self.estimated_time * developer_rate
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


# Work Log Model
class WorkLog(models.Model):
    class BillingStatus(models.TextChoices):
        BILLED = "billed", "Billed"
        PROCESSED = "processed", "Processed"
        UNBILLED = "unbilled", "Unbilled"

    class Status(models.TextChoices):
        REVIEW = "review", "Review"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"

    function = models.ForeignKey(
        Function, on_delete=models.CASCADE, related_name="work_logs"
    )
    developer = models.ForeignKey(
        User, on_delete=models.CASCADE, limit_choices_to={"role": "developer"}
    )
    date_logged = models.DateField(auto_now_add=True)
    hours_worked = models.DecimalField(max_digits=5, decimal_places=2)
    description = models.TextField()
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.REVIEW
    )
    reason = models.TextField(null=True, blank=True)
    billed_date = models.DateField(null=True, blank=True)
    processed_date = models.DateField(null=True, blank=True)
    billed_status = models.CharField(
        max_length=20,
        choices=BillingStatus.choices,
        default=BillingStatus.UNBILLED,
    )

    history = HistoricalRecords()


# Invoice Model
class Invoice(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        PAID = "paid", "Paid"
        DISPUTED = "disputed", "Disputed"

    id = models.AutoField(primary_key=True, unique=True, editable=False, db_index=True)
    client = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        limit_choices_to={"role": User.Role.CLIENT},
        related_name="invoices",
        null=True,
        blank=True,
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=Status.choices, default="pending")
    from_date = models.DateField(null=True, blank=True)
    to_date = models.DateField(null=True, blank=True)
    generated_date = models.DateField(auto_now_add=True)
    pdf_file = models.FileField(upload_to="invoices/pdfs/", null=True, blank=True)

    history = HistoricalRecords()
