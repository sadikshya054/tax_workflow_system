from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.http import FileResponse
from .forms import DocumentUploadForm,DocumentFeedbackForm, TaskForm,DocumentRequirementForm, TaxReturnForm, StaffTaxReturnReviewForm
from .models import Document, DocumentFeedback, Task,DocumentRequirement, Notification, TaxReturn, Notification
from django.contrib import messages

@login_required
def create_task(request):
    # Only Staff users can create tasks.
    if request.user.role != 'STAFF':
        return render(
            request,
            'documents/access_denied.html',
            status=403
        )

    if request.method == 'POST':
        # Processes the submitted task form.
        form = TaskForm(request.POST)

        if form.is_valid():
            # Saves the new task.
            task = form.save()

            # Creates a notification for the assigned Client.
            Notification.objects.create(
                recipient=task.assigned_to,
                message=f'You have a new task: {task.title}.',
                notification_type=Notification.NotificationType.TASK,
                task=task
            )
            # Returns Staff to the task list.
            return redirect('staff_tasks')

    else:
        # Displays an empty task form.
        form = TaskForm()

    return render(
        request,
        'documents/create_task.html',
        {'form': form}
    )


@login_required
def staff_tasks(request):
    # Only Staff users can access the Staff task management page.
    if request.user.role != 'STAFF':
        return render(
            request,
            'documents/access_denied.html',
            status=403
        )

    # Gets tasks that are still waiting for the Client to complete.
    pending_tasks = Task.objects.filter(
        status=Task.Status.PENDING
    ).select_related('assigned_to').order_by('-created_at')

    # Gets tasks that Clients have already completed.
    completed_tasks = Task.objects.filter(
        status=Task.Status.COMPLETED
    ).select_related('assigned_to').order_by('-created_at')

    return render(
        request,
        'documents/staff_tasks.html',
        {
            'pending_tasks': pending_tasks,
            'completed_tasks': completed_tasks,
        }
    )

@login_required
def delete_task(request, task_id):
    # Only Staff users can delete tasks.
    if request.user.role != 'STAFF':
        return render(
            request,
            'documents/access_denied.html',
            status=403
        )

    # Only allows deletion through a POST request.
    if request.method == 'POST':
        task = get_object_or_404(
            Task,
            id=task_id
        )

        # Deletes the selected task.
        task.delete()

    return redirect('staff_tasks')

@login_required
def my_tasks(request):
    # Only Client users can access their task list.
    if request.user.role != 'CLIENT':
        return render(
            request,
            'documents/access_denied.html',
            status=403
        )

    # Retrieves only tasks assigned to the logged-in Client.
    tasks = Task.objects.filter(
        assigned_to=request.user
    ).order_by('-created_at')

    return render(
        request,
        'documents/my_tasks.html',
        {'tasks': tasks}
    )


@login_required
@require_POST
def complete_task(request, task_id):
    # Only Client users can complete tasks.
    if request.user.role != 'CLIENT':
        return render(
            request,
            'documents/access_denied.html',
            status=403
        )

    # Gets only the task assigned to the logged-in Client.
    task = get_object_or_404(
        Task,
        id=task_id,
        assigned_to=request.user
    )

    # Changes the task status to Completed.
    task.status = Task.Status.COMPLETED
    task.save()

    # Returns the Client to their task list.
    return redirect('my_tasks')

@login_required
def upload_document(request):
    # Only Client accounts can upload documents.
    if request.user.role != 'CLIENT':
        return render(
            request,
            'documents/access_denied.html',
            status=403
        )

    if request.method == 'POST':
        # Processes the upload using the Client's own document requirements.
        form = DocumentUploadForm(
            request.POST,
            request.FILES,
            user=request.user
        )

        if form.is_valid():
            document = form.save(commit=False)

            # Assigns the document to the currently logged-in Client.
            document.owner = request.user

            # Confirms that the selected requirement belongs to this Client.
            if (
                document.requirement is None
                or document.requirement.client != request.user
            ):
                return render(
                    request,
                    'documents/access_denied.html',
                    status=403
                )

            # Saves the uploaded document.
            document.save()

            # Returns the Client to their document list.
            return redirect('my_documents')

    else:
        # Displays only requirements belonging to the logged-in Client.
        form = DocumentUploadForm(user=request.user)

    return render(
        request,
        'documents/upload.html',
        {'form': form}
    )

@login_required
def my_documents(request):
    # Only Client accounts can access their document list.
    if request.user.role != 'CLIENT':
        return render(
            request,
            'documents/access_denied.html',
            status=403
        )

    # Retrieves only requirements belonging to the logged-in Client.
    requirements = DocumentRequirement.objects.filter(
        client=request.user
    ).order_by('created_at')

    # Retrieves only documents owned by the logged-in Client.
    documents = Document.objects.filter(
        owner=request.user
    ).order_by('-uploaded_at')

    # Finds requirements that have not received an uploaded document.
    required_documents = requirements.filter(
        uploaded_documents__isnull=True
    )

    # Finds uploaded documents that have not been submitted yet.
    pending_documents = documents.filter(
        status=Document.Status.PENDING
    )

    # Finds documents that have been submitted and are waiting for review.
    awaiting_review = documents.filter(
        status=Document.Status.SUBMITTED
    )

    # Finds documents that Staff have already reviewed.
    reviewed_documents = documents.filter(
        status=Document.Status.REVIEWED
    )

    return render(
        request,
        'documents/my_documents.html',
        {
            'required_documents': required_documents,
            'pending_documents': pending_documents,
            'awaiting_review': awaiting_review,
            'reviewed_documents': reviewed_documents
        }
    )


@login_required
def document_detail(request, document_id):
    # Gets the requested document.
    document = get_object_or_404(
        Document,
        id=document_id
    )

    # Clients can only view their own documents.
    if request.user.role == 'CLIENT':
        if document.owner != request.user:
            return render(
                request,
                'documents/access_denied.html',
                status=403
            )

    # Staff can view documents that are submitted or already reviewed.
    elif request.user.role == 'STAFF':
        if document.status not in [
            Document.Status.SUBMITTED,
            Document.Status.REVIEWED
        ]:
            return render(
                request,
                'documents/access_denied.html',
                status=403
            )

    # Blocks users with an invalid or unsupported role.
    else:
        return render(
            request,
            'documents/access_denied.html',
            status=403
        )

    return render(
        request,
        'documents/document_detail.html',
        {
            'document': document
        }
    )

@login_required
def serve_document(request, document_id):
    # Gets the requested document.
    document = get_object_or_404(
        Document,
        id=document_id
    )

    # Clients can only open their own documents.
    if request.user.role == 'CLIENT':
        if document.owner != request.user:
            return render(
                request,
                'documents/access_denied.html',
                status=403
            )

    # Staff can open submitted and reviewed documents.
    elif request.user.role == 'STAFF':
        if document.status not in [
            Document.Status.SUBMITTED,
            Document.Status.REVIEWED
        ]:
            return render(
                request,
                'documents/access_denied.html',
                status=403
            )

    # Blocks users with an invalid or unsupported role.
    else:
        return render(
            request,
            'documents/access_denied.html',
            status=403
        )

    # Opens the protected document file.
    return FileResponse(
        document.file.open('rb'),
        as_attachment=False
    )

@login_required
def submit_document(request, document_id):
    # Only Client accounts can submit their own documents.
    if request.user.role != 'CLIENT':
        return render(
            request,
            'documents/access_denied.html',
            status=403
        )

    # Finds the document only if it belongs to the logged-in Client.
    document = get_object_or_404(
        Document,
        id=document_id,
        owner=request.user
    )

    # Changes the document status to Submitted.
    document.status = Document.Status.SUBMITTED
    document.save()

    # Returns the Client to their document list.
    return redirect('my_documents')

@login_required
def tax_return_details(request):
    # Only Clients can create and view their Tax Return.
    if request.user.role != 'CLIENT':
        return render(
            request,
            'documents/access_denied.html',
            status=403
        )

    # Gets the Client's existing draft Tax Return, if one exists.
    tax_return = TaxReturn.objects.filter(
        client=request.user,
        status=TaxReturn.Status.DRAFT
    ).first()

    # Stores upload errors so they can be shown beside the upload field.
    upload_error = None
    if request.method == 'POST':

        # Handles supporting document uploads.
        if 'upload_document' in request.POST:

            uploaded_file = request.FILES.get('supporting_document')

            # Creates a form using the information currently entered.
            form = TaxReturnForm(
                request.POST,
                instance=tax_return
            )

            if uploaded_file:

                # Allows common tax document file types.
                allowed_types = [
                    'application/pdf',
                    'image/jpeg',
                    'image/png',
                ]

                # Gets the file extension.
                file_extension = uploaded_file.name.lower().split('.')[-1]

                # Allows only approved file extensions.
                allowed_extensions = [
                    'pdf',
                    'jpg',
                    'jpeg',
                    'png',
                ]

                # Rejects unsupported file types.
                if (
                    uploaded_file.content_type not in allowed_types
                    or file_extension not in allowed_extensions
                ):
                    # Stores the error for display beside the upload field.
                    upload_error = 'Only PDF, JPG, and PNG files are allowed.'

                else:
                    # Limits uploaded files to 10 MB.
                    max_size = 10 * 1024 * 1024

                    # Rejects files larger than 10 MB.
                    if uploaded_file.size > max_size:
                        upload_error = 'File size must not exceed 10 MB.'

                    else:
                        # Saves the document without creating a Tax Return.
                        Document.objects.create(
                            owner=request.user,
                            tax_return=tax_return,
                            file=uploaded_file,
                            status=Document.Status.PENDING
                        )

            else:
                upload_error = 'Please select a document to upload.'

            # Gets documents currently linked to the Tax Return.
            if tax_return:
                supporting_documents = Document.objects.filter(
                    owner=request.user,
                    tax_return=tax_return
                ).order_by('-uploaded_at')
            else:
                # Shows documents uploaded before the Tax Return is created.
                supporting_documents = Document.objects.filter(
                    owner=request.user,
                    tax_return__isnull=True
                ).order_by('-uploaded_at')

            return render(
                request,
                'documents/tax_return_details.html',
                {
                    'form': form,
                    'tax_return': tax_return,
                    'supporting_documents': supporting_documents,
                    'upload_error': upload_error

                }
            )

        # Handles saving or submitting the Tax Return details.
        form = TaxReturnForm(
            request.POST,
            instance=tax_return
        )

        if form.is_valid():

            # Saves the Tax Return without committing the Client yet.
            tax_return = form.save(commit=False)

            # Links the Tax Return to the logged-in Client.
            tax_return.client = request.user

            if 'submit_tax_return' in request.POST:

                # Submits the Tax Return for Staff review.
                tax_return.status = TaxReturn.Status.SUBMITTED
                tax_return.save()

                # Submits all documents linked to this Tax Return for Staff review.
                Document.objects.filter(
                    owner=request.user,
                    tax_return=tax_return
                ).update(
                    status=Document.Status.SUBMITTED
                )

                # Also submits any documents uploaded before the Tax Return was created.
                Document.objects.filter(
                    owner=request.user,
                    tax_return__isnull=True
                ).update(
                    tax_return=tax_return,
                    status=Document.Status.SUBMITTED
                )

                # Tells the Client that the Tax Return was submitted successfully.
                messages.success(
                    request,
                    'Your Tax Return has been submitted successfully.'
                )

            else:

                # Saves the Tax Return as a draft.
                tax_return.status = TaxReturn.Status.DRAFT
                tax_return.save()

                # Links uploaded documents to this Tax Return.
                Document.objects.filter(
                    owner=request.user,
                    tax_return__isnull=True
                ).update(
                    tax_return=tax_return
                )

                messages.success(
                    request,
                    'Your Tax Return has been saved as a draft.'
                )

            return redirect('tax_return_details')

    else:
        form = TaxReturnForm(
            instance=tax_return
        )

    # Gets documents linked to the current Tax Return.
    if tax_return:
        supporting_documents = Document.objects.filter(
            owner=request.user,
            tax_return=tax_return
        ).order_by('-uploaded_at')
    else:
        # Gets documents uploaded before a Tax Return is saved.
        supporting_documents = Document.objects.filter(
            owner=request.user,
            tax_return__isnull=True
        ).order_by('-uploaded_at')

    return render(
        request,
        'documents/tax_return_details.html',
        {
            'form': form,
            'tax_return': tax_return,
            'supporting_documents': supporting_documents,
            'upload_error': upload_error

        }
    )


@login_required
def tax_return_outcome(request, tax_return_id):
    # Only Clients can view their Tax Return outcome.
    if request.user.role != 'CLIENT':
        return render(
            request,
            'documents/access_denied.html',
            status=403
        )

    # Allows the Client to view only their own completed or discarded Tax Return.
    tax_return = get_object_or_404(
        TaxReturn,
        id=tax_return_id,
        client=request.user,
        status__in=[
            TaxReturn.Status.COMPLETED,
            TaxReturn.Status.DISCARDED
        ]
    )

    # Displays the outcome for the selected Tax Return.
    return render(
        request,
        'documents/tax_return_outcome.html',
        {
            'tax_return': tax_return
        }
    )


@login_required
def my_tax_returns(request):
    # Only Clients can access their Tax Return history.
    if request.user.role != 'CLIENT':
        return render(
            request,
            'documents/access_denied.html',
            status=403
        )

    # Gets all Tax Returns belonging to the logged-in Client.
    tax_returns = TaxReturn.objects.filter(
        client=request.user
    ).order_by('-updated_at')

    return render(
        request,
        'documents/my_tax_returns.html',
        {
            'tax_returns': tax_returns
        }
    )

@login_required
def tax_return_status(request, tax_return_id):
    # Only Clients can view their Tax Return status.
    if request.user.role != 'CLIENT':
        return render(
            request,
            'documents/access_denied.html',
            status=403
        )

    # Gets the selected Tax Return belonging to the logged-in Client.
    # Allows the Client to view submitted, completed, and discarded returns.
    tax_return = get_object_or_404(
        TaxReturn,
        id=tax_return_id,
        client=request.user,
        status__in=[
            TaxReturn.Status.SUBMITTED,
            TaxReturn.Status.COMPLETED,
            TaxReturn.Status.DISCARDED
        ]
    )

    # Gets supporting documents linked to this Tax Return.
    supporting_documents = Document.objects.filter(
        tax_return=tax_return,
        owner=request.user
    ).order_by('-uploaded_at')

    return render(
        request,
        'documents/tax_return_status.html',
        {
            'tax_return': tax_return,
            'supporting_documents': supporting_documents
        }
    )

@login_required
def staff_documents(request):
    # Only Staff users can access the Staff document management page.
    if request.user.role != 'STAFF':
        return render(
            request,
            'documents/access_denied.html',
            status=403
        )

    # Gets the selected filter values from the page.
    selected_client = request.GET.get('client', '')
    selected_status = request.GET.get('status', '')

    # Starts with submitted and reviewed documents only.
    documents = Document.objects.filter(
        status__in=[
            Document.Status.SUBMITTED,
            Document.Status.REVIEWED
        ]
    ).select_related('owner').order_by('-uploaded_at')

    # Filters documents by Client username.
    if selected_client:
        documents = documents.filter(
            owner__username=selected_client
        )

    # Filters documents by document status.
    if selected_status:
        documents = documents.filter(
            status=selected_status
        )

    # Separates the filtered documents into two sections.
    submitted_documents = documents.filter(
        status=Document.Status.SUBMITTED
    )

    reviewed_documents = documents.filter(
        status=Document.Status.REVIEWED
    )

    # Gets all Client accounts for the username filter.
    clients = request.user.__class__.objects.filter(
        role=request.user.Role.CLIENT
    ).order_by('username')

    return render(
        request,
        'documents/staff_documents.html',
        {
            'submitted_documents': submitted_documents,
            'reviewed_documents': reviewed_documents,
            'clients': clients,
            'selected_client': selected_client,
            'selected_status': selected_status,
        }
    )

@login_required
@require_POST
def mark_as_reviewed(request, document_id):
    # Only Staff users can mark documents as reviewed.
    if request.user.role != 'STAFF':
        return render(
            request,
            'documents/access_denied.html',
            status=403
        )

    # Finds the document only if it has been submitted for review.
    document = get_object_or_404(
        Document,
        id=document_id,
        status=Document.Status.SUBMITTED
    )

    # Changes the document status to Reviewed.
    document.status = Document.Status.REVIEWED
    document.save()

    # Notifies the Client that Staff has reviewed the document.
    Notification.objects.create(
        recipient=document.owner,
        message=f'Your document has been reviewed: {document.file.name}.',
        notification_type=Notification.NotificationType.REVIEWED,
        document=document
    )

    # Returns Staff to the submitted documents page.
    return redirect('staff_documents')

@login_required
@require_POST
def add_feedback(request, document_id):
    # Only Staff users can add feedback.
    if request.user.role != 'STAFF':
        return render(
            request,
            'documents/access_denied.html',
            status=403
        )

    # Finds the document only if it has been submitted or reviewed.
    document = get_object_or_404(
        Document,
        id=document_id,
        status__in=[
            Document.Status.SUBMITTED,
            Document.Status.REVIEWED
        ]
    )

    # Processes the feedback submitted by Staff.
    form = DocumentFeedbackForm(request.POST)

    if form.is_valid():
        feedback = form.save(commit=False)

        # Links the feedback to the current document.
        feedback.document = document

        # Records the Staff member who provided the feedback.
        feedback.staff = request.user

        feedback.save()

        # Notifies the Client that Staff has added feedback.
        Notification.objects.create(
            recipient=document.owner,
            message=f'Staff has added feedback to your document: {document.file.name}.',
            notification_type=Notification.NotificationType.FEEDBACK,
            document=document
        )
        
    # Returns Staff to the submitted documents page.
    return redirect('staff_documents')

@login_required
def document_requirements(request):
    # Only Staff users can manage document requirements.
    if request.user.role != 'STAFF':
        return render(
            request,
            'documents/access_denied.html',
            status=403
        )

    if request.method == 'POST':
        # Processes the submitted document requirement form.
        form = DocumentRequirementForm(request.POST)

        if form.is_valid():
            # Saves the new document requirement.
            requirement = form.save()

            # Creates a notification for the selected Client.
            Notification.objects.create(
                recipient=requirement.client,
                message=f'You have a new document requirement: {requirement.document_name}.',
                notification_type=Notification.NotificationType.REQUIREMENT,
                requirement=requirement
            )

            # Returns Staff to the requirements page.
            return redirect('document_requirements')

    else:
        # Displays an empty form when Staff opens the page.
        form = DocumentRequirementForm()

    # Retrieves all document requirements for the Staff page.
    requirements = DocumentRequirement.objects.all().order_by('-created_at')

    return render(
        request,
        'documents/document_requirements.html',
        {
            'form': form,
            'requirements': requirements
        }
    )

@login_required
def delete_document_requirement(request, requirement_id):
    # Only Staff users can delete document requirements.
    if request.user.role != 'STAFF':
        return render(
            request,
            'documents/access_denied.html',
            status=403
        )

    # Only allows deletion through a POST request.
    if request.method == 'POST':
        requirement = get_object_or_404(
            DocumentRequirement,
            id=requirement_id
        )

        # Deletes the selected document requirement.
        requirement.delete()

    return redirect('document_requirements')


@login_required
@require_POST
def mark_notification_read(request, notification_id):
    # Only Client users can access their notifications.
    if request.user.role != 'CLIENT':
        return render(
            request,
            'documents/access_denied.html',
            status=403
        )

    # Finds only the notification belonging to the logged-in Client.
    notification = get_object_or_404(
        Notification,
        id=notification_id,
        recipient=request.user
    )

    # Marks the notification as read.
    notification.is_read = True
    notification.save()

    # Sends the Client to the relevant page.
    if notification.notification_type == Notification.NotificationType.REQUIREMENT:
        return redirect('my_documents')

    elif notification.notification_type in [
        Notification.NotificationType.FEEDBACK,
        Notification.NotificationType.REVIEWED
    ]:
        return redirect(
            'document_detail',
            document_id=notification.document.id
        )

    elif notification.notification_type == Notification.NotificationType.TASK:
        return redirect('my_tasks')

    elif notification.notification_type == Notification.NotificationType.TAX_RETURN:
        return redirect(
            'tax_return_outcome',
            tax_return_id=notification.tax_return.id
        )

    # Uses the Client Dashboard as a safe fallback.
    return redirect('client_dashboard')


@login_required
def staff_tax_returns(request):
    # Only Staff can access Tax Returns.
    if request.user.role != 'STAFF':
        return render(
            request,
            'documents/access_denied.html',
            status=403
        )

    # Gets Tax Returns waiting for Staff review.
    submitted_tax_returns = TaxReturn.objects.filter(
        status=TaxReturn.Status.SUBMITTED
    ).select_related('client').order_by('-updated_at')

    # Gets Tax Returns that Staff have already completed.
    completed_tax_returns = TaxReturn.objects.filter(
        status=TaxReturn.Status.COMPLETED
    ).select_related('client').order_by('-updated_at')

    # Gets Tax Returns that Staff have discarded.
    discarded_tax_returns = TaxReturn.objects.filter(
        status=TaxReturn.Status.DISCARDED
    ).select_related('client').order_by('-updated_at')

    return render(
    request,
    'documents/staff_tax_returns.html',
    {
        'submitted_tax_returns': submitted_tax_returns,
        'completed_tax_returns': completed_tax_returns,
        'discarded_tax_returns': discarded_tax_returns,
    }
)

@login_required
def staff_tax_return_detail(request, tax_return_id):
    # Only Staff can access Tax Return details.
    if request.user.role != 'STAFF':
        return render(
            request,
            'documents/access_denied.html',
            status=403
        )

    # Allows Staff to view both submitted and completed Tax Returns.
    tax_return = get_object_or_404(
        TaxReturn.objects.select_related('client'),
        id=tax_return_id
    )

    # Handles Staff reviewing a submitted Tax Return.
    if request.method == 'POST':

        # Completed Tax Returns cannot be edited again.
        if tax_return.status == TaxReturn.Status.COMPLETED:
            return render(
                request,
                'documents/access_denied.html',
                status=403
            )

        # Creates the review form using the Staff's submitted information.
        form = StaffTaxReturnReviewForm(
            request.POST,
            instance=tax_return
        )

        if form.is_valid():

            # Saves the Staff's review information.
            tax_return = form.save(commit=False)

            # Marks the Tax Return as completed after Staff review.
            tax_return.status = TaxReturn.Status.COMPLETED

            # Saves the completed Tax Return.
            tax_return.save()

            # Creates a notification for the Client.
            Notification.objects.create(
                recipient=tax_return.client,
                message=f"Your Tax Return for {tax_return.financial_year} has been completed.",
                notification_type=Notification.NotificationType.TAX_RETURN,
                tax_return=tax_return
            )

            # Returns Staff to the Tax Returns list.
            return redirect('staff_tax_returns')

    else:
        # Shows the review form only for submitted Tax Returns.
        if tax_return.status == TaxReturn.Status.SUBMITTED:
            form = StaffTaxReturnReviewForm(
                instance=tax_return
            )
        else:
            form = None

    # Gets supporting documents linked to this Tax Return.
    supporting_documents = Document.objects.filter(
        tax_return=tax_return
    ).select_related('owner').order_by('-uploaded_at')

    return render(
        request,
        'documents/staff_tax_return_detail.html',
        {
            'tax_return': tax_return,
            'supporting_documents': supporting_documents,
            'form': form
        }
    )

@login_required
@require_POST
def discard_tax_return(request, tax_return_id):
    # Only Staff users can discard Tax Returns.
    if request.user.role != 'STAFF':
        return render(
            request,
            'documents/access_denied.html',
            status=403
        )

    # Gets only a Tax Return that is currently waiting for review.
    tax_return = get_object_or_404(
        TaxReturn,
        id=tax_return_id,
        status=TaxReturn.Status.SUBMITTED
    )

    # Changes the status instead of deleting the Tax Return.
    tax_return.status = TaxReturn.Status.DISCARDED
    tax_return.save()

    # Notifies the Client that their Tax Return was discarded.
    Notification.objects.create(
        recipient=tax_return.client,
        message=f'Your Tax Return for {tax_return.financial_year} has been discarded. Please contact the tax practice if you need further assistance.',
        notification_type=Notification.NotificationType.TAX_RETURN,
        tax_return=tax_return
    )

    # Returns Staff to the Tax Returns page.
    return redirect('staff_tax_returns')