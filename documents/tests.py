from django.test import TestCase
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from accounts.models import User
from documents.models import Document, TaxReturn, Notification

class TaxReturnSecurityTests(TestCase):
    # Creates separate Client and Staff accounts for each test.
    def setUp(self):
        self.client_user = User.objects.create_user(
            username='test_client',
            password='testpassword123',
            role=User.Role.CLIENT
        )

        self.other_client = User.objects.create_user(
            username='other_client',
            password='testpassword123',
            role=User.Role.CLIENT
        )

        self.staff_user = User.objects.create_user(
            username='test_staff',
            password='testpassword123',
            role=User.Role.STAFF
        )

        # Creates a completed Tax Return belonging to the first Client.
        self.tax_return = TaxReturn.objects.create(
            client=self.client_user,
            financial_year='2025-26',
            tfn='123456789',
            address='Test Address',
            status=TaxReturn.Status.COMPLETED,
            estimated_refund=700.00,
            staff_notes='Your Tax Return has been reviewed.'
        )

    # Confirms that a Client can view their own completed Tax Return.
    def test_client_can_view_own_completed_tax_return(self):
        self.client.login(
            username='test_client',
            password='testpassword123'
        )

        response = self.client.get(
            reverse(
                'tax_return_outcome',
                args=[self.tax_return.id]
            )
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Your Tax Return has been reviewed.')

    # Confirms that a Client cannot view another Client's Tax Return.
    def test_client_cannot_view_another_clients_tax_return(self):
        self.client.login(
            username='other_client',
            password='testpassword123'
        )

        response = self.client.get(
            reverse(
                'tax_return_outcome',
                args=[self.tax_return.id]
            )
        )

        self.assertEqual(response.status_code, 404)

    # Confirms that Staff cannot use the Client outcome page.
    def test_staff_cannot_access_client_tax_return_outcome(self):
        self.client.login(
            username='test_staff',
            password='testpassword123'
        )

        response = self.client.get(
            reverse(
                'tax_return_outcome',
                args=[self.tax_return.id]
            )
        )

        self.assertEqual(response.status_code, 403)

    # Confirms that a Client cannot access the Staff Tax Return list.
    def test_client_cannot_access_staff_tax_return_list(self):
        self.client.login(
            username='test_client',
            password='testpassword123'
        )

        response = self.client.get(
            reverse('staff_tax_returns')
        )

        self.assertEqual(response.status_code, 403)
        

    # Confirms that a Client can view their own submitted Tax Return status.
    def test_client_can_view_own_submitted_tax_return_status(self):

        # Changes the Tax Return to submitted for this test.
        self.tax_return.status = TaxReturn.Status.SUBMITTED
        self.tax_return.save()

        # Logs in as the Client who owns the Tax Return.
        self.client.login(
            username='test_client',
            password='testpassword123'
        )

        # Opens the Client's own submitted Tax Return status page.
        response = self.client.get(
            reverse(
                'tax_return_status',
                args=[self.tax_return.id]
            )
        )

        # The Client should be allowed to view their own status.
        self.assertEqual(response.status_code, 200)


    # Confirms that a Client cannot view another Client's Tax Return status.
    def test_client_cannot_view_another_clients_tax_return_status(self):

        # Changes the Tax Return to submitted for this test.
        self.tax_return.status = TaxReturn.Status.SUBMITTED
        self.tax_return.save()

        # Logs in as a different Client.
        self.client.login(
            username='other_client',
            password='testpassword123'
        )

        # Tries to access another Client's Tax Return status.
        response = self.client.get(
            reverse(
                'tax_return_status',
                args=[self.tax_return.id]
            )
        )

        # Access should be denied because the Tax Return belongs to another Client.
        self.assertEqual(response.status_code, 404)

class TaxReturnNotificationTests(TestCase):
    # Creates a Client, another Client, Staff and a completed Tax Return.
    def setUp(self):
        self.client_user = User.objects.create_user(
            username='notification_client',
            password='testpassword123',
            role=User.Role.CLIENT
        )

        self.other_client = User.objects.create_user(
            username='other_notification_client',
            password='testpassword123',
            role=User.Role.CLIENT
        )

        self.tax_return = TaxReturn.objects.create(
            client=self.client_user,
            financial_year='2025-26',
            tfn='987654321',
            address='Test Address',
            status=TaxReturn.Status.COMPLETED,
            estimated_refund=500.00
        )

        self.notification = Notification.objects.create(
            recipient=self.client_user,
            message='Your Tax Return has been completed.',
            notification_type=Notification.NotificationType.TAX_RETURN,
            tax_return=self.tax_return
        )

    # Confirms that clicking a Tax Return notification marks it as read
    # and redirects the Client to the correct outcome page.
    def test_tax_return_notification_opens_outcome(self):
        self.client.login(
            username='notification_client',
            password='testpassword123'
        )

        response = self.client.post(
            reverse(
                'mark_notification_read',
                args=[self.notification.id]
            )
        )

        self.notification.refresh_from_db()

        self.assertTrue(self.notification.is_read)
        self.assertRedirects(
            response,
            reverse(
                'tax_return_outcome',
                args=[self.tax_return.id]
            )
        )

    # Confirms that a Client cannot mark another Client's notification as read.
    def test_client_cannot_access_another_clients_notification(self):
        self.client.login(
            username='other_notification_client',
            password='testpassword123'
        )

        response = self.client.post(
            reverse(
                'mark_notification_read',
                args=[self.notification.id]
            )
        )

        self.assertEqual(response.status_code, 404)

# Tests that uploaded documents are protected from unauthorised access.
class DocumentSecurityTests(TestCase):
    # Creates two Clients, a Staff user and a submitted document.
    def setUp(self):
        self.client_user = User.objects.create_user(
            username='document_client',
            password='testpassword123',
            role=User.Role.CLIENT
        )

        self.other_client = User.objects.create_user(
            username='other_document_client',
            password='testpassword123',
            role=User.Role.CLIENT
        )

        self.staff_user = User.objects.create_user(
            username='document_staff',
            password='testpassword123',
            role=User.Role.STAFF
        )

        # Creates a test PDF document owned by the first Client.
        test_file = SimpleUploadedFile(
            'test_document.pdf',
            b'%PDF-1.4 test document',
            content_type='application/pdf'
        )

        self.document = Document.objects.create(
            owner=self.client_user,
            file=test_file,
            status=Document.Status.SUBMITTED
        )

    # Confirms that a Client can view their own document.
    def test_client_can_view_own_document(self):
        self.client.login(
            username='document_client',
            password='testpassword123'
        )

        response = self.client.get(
            reverse(
                'document_detail',
                args=[self.document.id]
            )
        )

        self.assertEqual(response.status_code, 200)

    # Confirms that a Client cannot view another Client's document.
    def test_client_cannot_view_another_clients_document(self):
        self.client.login(
            username='other_document_client',
            password='testpassword123'
        )

        response = self.client.get(
            reverse(
                'document_detail',
                args=[self.document.id]
            )
        )

        self.assertEqual(response.status_code, 403)

    # Confirms that Staff can view a submitted document.
    def test_staff_can_view_submitted_document(self):
        self.client.login(
            username='document_staff',
            password='testpassword123'
        )

        response = self.client.get(
            reverse(
                'document_detail',
                args=[self.document.id]
            )
        )

        self.assertEqual(response.status_code, 200
        )

    # Confirms that a Client cannot access the Staff Client list.
    def test_client_cannot_access_staff_clients_page(self):
        self.client.login(
            username='document_client',
            password='testpassword123'
        )

        response = self.client.get(
            reverse('staff_clients')
        )

        self.assertEqual(response.status_code, 403)

    def test_client_can_view_own_document(self):
        # Client can access their own protected document.
        self.client.login(
            username='document_client',
            password='testpassword123'
        )

        response = self.client.get(
            reverse('serve_document', args=[self.document.id])
        )

        self.assertEqual(response.status_code, 200)

    def test_client_cannot_view_other_client_document(self):
        # Client cannot access another client's document.
        other_file = SimpleUploadedFile(
            'other_document.pdf',
            b'%PDF-1.4 other test document',
            content_type='application/pdf'
        )

        other_document = Document.objects.create(
            owner=self.other_client,
            file=other_file,
            status=Document.Status.SUBMITTED
        )

        self.client.login(
            username='document_client',
            password='testpassword123'
        )

        response = self.client.get(
            reverse('serve_document', args=[other_document.id])
        )

        self.assertEqual(response.status_code, 403)

    def test_staff_can_view_submitted_document(self):
        # Staff can access a submitted document.
        self.client.login(
            username='document_staff',
            password='testpassword123'
        )

        response = self.client.get(
            reverse('serve_document', args=[self.document.id])
        )

        self.assertEqual(response.status_code, 200)

    def test_logged_out_user_cannot_view_document(self):
        # Logged-out users must sign in first.
        response = self.client.get(
            reverse('serve_document', args=[self.document.id])
        )

        self.assertEqual(response.status_code, 302)

    def test_client_cannot_upload_invalid_file_type(self):
        # Client cannot upload an unsupported file type.
        self.client.login(
            username='document_client',
            password='testpassword123'
        )

        invalid_file = SimpleUploadedFile(
            'test_file.exe',
            b'fake executable file',
            content_type='application/x-msdownload'
        )

        response = self.client.post(
            reverse('upload_document'),
            {
                'file': invalid_file,
            }
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            'Only PDF, JPG, and PNG files are allowed.'
        )

    def test_client_cannot_upload_file_over_10mb(self):
        # Client cannot upload a file larger than 10 MB.
        self.client.login(
            username='document_client',
            password='testpassword123'
        )

        large_file = SimpleUploadedFile(
            'large_file.pdf',
            b'0' * (10 * 1024 * 1024 + 1),
            content_type='application/pdf'
        )

        response = self.client.post(
            reverse('upload_document'),
            {
                'file': large_file,
            }
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            'File size must not exceed 10 MB.'
        )

    def test_client_cannot_upload_invalid_supporting_document(self):
        # Rejects unsupported file types from the Tax Return page.
        self.client.login(
            username='document_client',
            password='testpassword123'
        )

        invalid_file = SimpleUploadedFile(
            'malicious.exe',
            b'test executable file',
            content_type='application/octet-stream'
        )

        response = self.client.post(
            reverse('tax_return_details'),
            {
                'upload_document': 'Upload Document',
                'supporting_document': invalid_file,
            }
        )

        self.assertEqual(response.status_code, 302)

        self.assertFalse(
            Document.objects.filter(
                file__endswith='.exe'
            ).exists()
        )


    def test_client_cannot_upload_oversized_supporting_document(self):
        # Rejects supporting documents larger than 10 MB.
        self.client.login(
            username='document_client',
            password='testpassword123'
        )

        oversized_file = SimpleUploadedFile(
            'large_document.pdf',
            b'x' * (10 * 1024 * 1024 + 1),
            content_type='application/pdf'
        )

        response = self.client.post(
            reverse('tax_return_details'),
            {
                'upload_document': 'Upload Document',
                'supporting_document': oversized_file,
            }
        )

        self.assertEqual(response.status_code, 302)

        # Confirms the oversized file was not saved.
        self.assertFalse(
            Document.objects.filter(
                file__endswith='large_document.pdf'
            ).exists()
        )