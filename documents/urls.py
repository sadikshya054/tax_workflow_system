from django.urls import path
from . import views

urlpatterns = [
    # Allows Clients to upload documents.
    path(
        'upload/',
        views.upload_document,
        name='upload_document'
    ),

    # Shows only documents owned by the logged-in Client.
    path(
        'my-documents/',
        views.my_documents,
        name='my_documents'
    ),

    #Opens the Client tax return details form.
    path(
        'tax-return/', 
        views.tax_return_details, 
        name='tax_return_details'
    ),

    # Opens the Client's Tax Return history.
    path(
        'my-tax-returns/',
        views.my_tax_returns,
        name='my_tax_returns'
    ),

    # Opens the status of a submitted Tax Return.
    path(
        'tax-return/<int:tax_return_id>/status/',
        views.tax_return_status,
        name='tax_return_status'
    ),

    # Opens the completed Tax Return outcome for the Client.
    path(
        'tax-return/<int:tax_return_id>/outcome/',
        views.tax_return_outcome,
        name='tax_return_outcome'
    ),

    # Displays an individual document only to its owner.
    path(
        '<int:document_id>/',
        views.document_detail,
        name='document_detail'
    ),

    # Allows a Client to submit their own document for Staff review.
    path(
        '<int:document_id>/submit/',
        views.submit_document,
        name='submit_document'
    ),

    path(
        'view/<int:document_id>/', 
        views.serve_document, 
        name='serve_document'
    ),

    # Allows Staff to mark a submitted document as reviewed.
    path(
        '<int:document_id>/mark-reviewed/',
        views.mark_as_reviewed,
        name='mark_as_reviewed'
    ),

    # Allows Staff to add feedback to a submitted or reviewed document.
    path(
        '<int:document_id>/feedback/',
        views.add_feedback,
        name='add_feedback'
    ),

    # Displays submitted documents for Staff to review.
    path(
        'staff/',
        views.staff_documents,
        name='staff_documents'
    ),

    # Opens the Staff Tax Return review page.
    path(
        'staff/tax-returns/', 
        views.staff_tax_returns, 
        name='staff_tax_returns'
    ),

    # Opens one submitted Tax Return for Staff review.
    path(
        'staff/tax-returns/<int:tax_return_id>/',
        views.staff_tax_return_detail,
        name='staff_tax_return_detail'
    ),

    # Allows Staff to discard a submitted Tax Return.
    path(
        'staff/tax-returns/<int:tax_return_id>/discard/',
        views.discard_tax_return,
        name='discard_tax_return'
    ),
    
    # Allows Staff to create a new task.
    path(
        'tasks/create/',
        views.create_task,
        name='create_task'
    ),

    # Displays tasks for Staff.
    path(
        'tasks/',
        views.staff_tasks,
        name='staff_tasks'
    ),

    path(
        'tasks/<int:task_id>/delete/',
        views.delete_task,
        name='delete_task'
    ),

    # Allows Staff to manage document requirements for Clients.
    path(
        'requirements/',
        views.document_requirements,
        name='document_requirements'
    ),

    path(
        'requirements/<int:requirement_id>/delete/',
        views.delete_document_requirement,
        name='delete_document_requirement'
    ),

    # Displays tasks assigned to the logged-in Client.
    path(
        'my-tasks/',
        views.my_tasks,
        name='my_tasks'
    ),

    # Allows a Client to mark their assigned task as completed.
    path(
        'my-tasks/<int:task_id>/complete/',
        views.complete_task,
        name='complete_task'
    ),

    # Allows Clients to mark their notifications as read.
    path(
        'notifications/<int:notification_id>/read/',
        views.mark_notification_read,
        name='mark_notification_read'
    ),

]