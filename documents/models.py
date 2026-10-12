from django.conf import settings
from django.db import models


class Document(models.Model):
    # Defines the possible stages of a document in the workflow.
    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        SUBMITTED = 'SUBMITTED', 'Submitted'
        REVIEWED = 'REVIEWED', 'Reviewed'

    # Links each document to the user who owns it.
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='documents'
    )

    # Links the document to the Client's tax return submission.
    tax_return = models.ForeignKey(
        'TaxReturn',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='documents'
    )
    
    # Links an uploaded document to its required document type.
    requirement = models.ForeignKey(
        'DocumentRequirement',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='uploaded_documents'
    )

    # Stores the uploaded document file.
    file = models.FileField(upload_to='documents/')

    # Stores the document's current workflow status.
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )

    # Records when the document was uploaded.
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        # Displays the document owner and file name in Django Admin.
        return f"{self.owner.username} - {self.file.name}"

class DocumentFeedback(models.Model):
    # Links the feedback to the document being reviewed.
    document = models.ForeignKey(
        Document,
        on_delete=models.CASCADE,
        related_name='feedback'
    )

    # Links the feedback to the Staff user who provided it.
    staff = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='document_feedback'
    )

    # Stores the feedback message written by Staff.
    message = models.TextField()

    # Records when the feedback was added.
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        # Displays the document and Staff member in Django Admin.
        return f"Feedback for {self.document.file.name} by {self.staff.username}"

class Task(models.Model):
    # Defines the possible stages of a task.
    class Status(models.TextChoices):
        # Task is waiting for the Client to complete.
        PENDING = 'PENDING', 'Pending'

        # Client has completed the task.
        COMPLETED = 'COMPLETED', 'Completed'

    # Stores the task title.
    title = models.CharField(max_length=200)

    # Stores more information about the task.
    description = models.TextField(blank=True)

    # Assigns the task to a Client.
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='assigned_tasks'
    )

    # Records the current task status.
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )

    # Records when the task was created.
    created_at = models.DateTimeField(auto_now_add=True)

    # Records the optional task due date.
    due_date = models.DateField(null=True, blank=True)

    def __str__(self):
        # Displays the task title and assigned Client.
        return f"{self.title} - {self.assigned_to.username}"

class DocumentRequirement(models.Model):
    # Stores a document that Staff requires from a Client.
    client = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='document_requirements'
    )

    # Stores the name of the required document.
    document_name = models.CharField(max_length=200)

    # Stores additional information about the requirement.
    description = models.TextField(blank=True)

    # Records when the requirement was created.
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        # Displays the required document and Client.
        return f"{self.document_name} - {self.client.username}"

class Notification(models.Model):
    # Defines the types of notifications shown to Clients.
    class NotificationType(models.TextChoices):
        REQUIREMENT = 'REQUIREMENT', 'Document Requirement'
        FEEDBACK = 'FEEDBACK', 'Staff Feedback'
        REVIEWED = 'REVIEWED', 'Document Reviewed'
        TASK = 'TASK', 'Task Assigned'
        TAX_RETURN = 'TAX_RETURN', 'Tax Return Completed'

    # Identifies the Client who should receive the notification.
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications'
    )

    # Stores the notification message.
    message = models.CharField(max_length=255)

    # Stores the type of notification.
    notification_type = models.CharField(
        max_length=20,
        choices=NotificationType.choices
    )

    # Tracks whether the Client has read the notification.
    is_read = models.BooleanField(default=False)

    # Records when the notification was created.
    created_at = models.DateTimeField(auto_now_add=True)

    # Optionally links the notification to a document.
    document = models.ForeignKey(
        Document,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='notifications'
    )

    # Optionally links the notification to a task.
    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='notifications'
    )

    # Optionally links the notification to a document requirement.
    requirement = models.ForeignKey(
        DocumentRequirement,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='notifications'
    )

    # Links the notification to the completed Tax Return.
    tax_return = models.ForeignKey(
        'TaxReturn',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='notifications'
    )

    def __str__(self):
        # Displays the recipient and notification message in Django Admin.
        return f"{self.recipient.username} - {self.message}"

class TaxReturn(models.Model):
    # Defines the possible stages of a tax return.
    class Status(models.TextChoices):
        # Tax Return is still being prepared by the Client.
        DRAFT = 'DRAFT', 'Draft'

        # Tax Return has been submitted for Staff review.
        SUBMITTED = 'SUBMITTED', 'Submitted'

        # Staff has finished reviewing the Tax Return.
        COMPLETED = 'COMPLETED', 'Completed'

        # Staff has decided not to proceed with this submission.
        DISCARDED = 'DISCARDED', 'Discarded'

    # Links the tax return to the Client who submitted it.
    client = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='tax_returns'
    )

    # Stores the financial year for the tax return.
    financial_year = models.CharField(max_length=9)

    # Stores the Client's Tax File Number.
    tfn = models.CharField(max_length=20)

    # Stores the optional Australian Business Number.
    abn = models.CharField(max_length=20, blank=True)

    # Stores the Client's residential or mailing address.
    address = models.TextField()

    # Stores the Client's total income.
    total_income = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True
    )

    # Stores the tax already withheld from the Client's income.
    tax_withheld = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True
    )

    # Stores the deductions provided by the Client.
    deductions = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True
    )

    # Stores additional information provided by the Client.
    client_notes = models.TextField(blank=True)

    # Stores the current stage of the tax return.
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT
    )

    # Stores the estimated refund calculated by Staff.
    estimated_refund = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True
    )

    # Stores an estimated amount payable if the Client owes tax.
    estimated_amount_payable = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True
    )

    # Stores additional notes from Staff.
    staff_notes = models.TextField(blank=True)

    # Records when the tax return was created.
    created_at = models.DateTimeField(auto_now_add=True)

    # Records when the tax return was last updated.
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        # Displays the Client and financial year in Django Admin.
        return f"{self.client.username} - {self.financial_year}"
