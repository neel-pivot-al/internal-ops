from django.db import models

from authentication.models import User

# Create your models here.


class Company(models.Model):
    name = models.CharField(max_length=255)
    website = models.URLField(blank=True, null=True)
    industry = models.CharField(max_length=255, blank=True)
    notes = models.TextField(blank=True)


class LeadStage(models.Model):
    name = models.CharField(
        help_text="e.g. Contacted, Demo Scheduled, Negotiation", max_length=100
    )
    order = models.PositiveIntegerField()


class Lead(models.Model):
    full_name = models.CharField(max_length=255)
    email = models.EmailField()
    position = models.CharField(max_length=255, blank=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    sales_manager = models.ForeignKey(
        "User",
        on_delete=models.CASCADE,
        related_name="leads",
        limit_choices_to={"role": User.Role.SALES_MANAGER},
    )
    current_stage = models.ForeignKey(
        "LeadStage", on_delete=models.SET_NULL, null=True, blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)


class Interaction(models.Model):
    class Platform(models.TextChoices):
        EMAIL = "email", "Email"
        LINKEDIN = "linkedin", "LinkedIn"
        TWITTER = "twitter", "Twitter"

    class Direction(models.TextChoices):
        INBOUND = "inbound", "Inbound"
        OUTBOUND = "outbound", "Outbound"

    lead = models.ForeignKey(Lead, on_delete=models.CASCADE)
    platform = models.CharField(max_length=50, choices=Platform.choices)
    message = models.TextField()
    direction = models.CharField(max_length=10, choices=Direction.choices)
    timestamp = models.DateTimeField(auto_now_add=True)
    platform_message_id = models.CharField(
        max_length=255, blank=True, null=True
    )  # for syncing


class Workflow(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)


class WorkflowStep(models.Model):
    workflow = models.ForeignKey(Workflow, on_delete=models.CASCADE)
    step_name = models.CharField(max_length=255)
    trigger_event = models.CharField(
        help_text="e.g. 'message_received', 'no_reply_3_days'", max_length=255
    )
    next_event = models.CharField(
        help_text="e.g. 'send_followup', 'send_reminder'",
        max_length=255,
    )
    delay_days = models.PositiveIntegerField(
        help_text="Delay before executing the next event in days from trigger",
    )
    order = models.PositiveIntegerField()


class Event(models.Model):
    lead = models.ForeignKey(Lead, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    event_type = models.CharField(max_length=255)
    planned_for = models.DateTimeField()
    completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
