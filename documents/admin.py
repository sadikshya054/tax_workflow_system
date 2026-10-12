from django.contrib import admin
from .models import Document, DocumentFeedback, Task, DocumentRequirement, TaxReturn

admin.site.register(TaxReturn)

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('owner', 'file', 'status', 'uploaded_at')


@admin.register(DocumentFeedback)
class DocumentFeedbackAdmin(admin.ModelAdmin):
    list_display = ('document', 'staff', 'created_at')


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'assigned_to', 'status', 'due_date', 'created_at')


@admin.register(DocumentRequirement)
class DocumentRequirementAdmin(admin.ModelAdmin):
    # Displays important requirement information in Django Admin.
    list_display = ('document_name', 'client', 'created_at')

