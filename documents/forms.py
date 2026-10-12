from django import forms
from .models import Document, DocumentFeedback, Task, DocumentRequirement, TaxReturn

class DocumentUploadForm(forms.ModelForm):
    # Allows Clients to upload a document linked to a Tax Return and requirement.
    class Meta:
        model = Document
        fields = ['requirement', 'file']
        labels = {
            'requirement': 'Document Type',
            'file': 'Upload File',
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if user is not None:
            # Shows document requirements created for this Client.
            self.fields['requirement'].queryset = (
                DocumentRequirement.objects.filter(
                    client=user
                ).order_by('created_at')
            )

    def clean_file(self):
        # Gets the uploaded file.
        file = self.cleaned_data.get('file')

        if file:
            # Allows only PDF, JPG and PNG files.
            allowed_types = [
                'application/pdf',
                'image/jpeg',
                'image/png',
            ]

            # Gets the file extension.
            file_extension = file.name.lower().split('.')[-1]

            # Allows only the approved extensions.
            allowed_extensions = [
                'pdf',
                'jpg',
                'jpeg',
                'png',
            ]

            # Rejects unsupported file types.
            if (
                file.content_type not in allowed_types
                or file_extension not in allowed_extensions
            ):
                raise forms.ValidationError(
                    'Only PDF, JPG, and PNG files are allowed.'
                )

            # Limits uploaded files to 10 MB.
            max_size = 10 * 1024 * 1024

            if file.size > max_size:
                raise forms.ValidationError(
                    'File size must not exceed 10 MB.'
                )

        return file

class DocumentFeedbackForm(forms.ModelForm):
    # Allows Staff to enter feedback about a document.
    class Meta:
        model = DocumentFeedback
        fields = ['message']

        # Adds a helpful label and placeholder to the feedback field.
        widgets = {
            'message': forms.Textarea(
                attrs={
                    'placeholder': 'Enter feedback for the Client...',
                    'rows': 4
                }
            )
        }
        

class TaskForm(forms.ModelForm):
    # Allows Clients to provide their tax return information.
    def clean_tfn(self):
        # Gets the TFN entered by the Client.
        tfn = self.cleaned_data.get('tfn')

        # Makes sure the TFN contains numbers only.
        if tfn and not tfn.isdigit():
            raise forms.ValidationError(
                'TFN must contain numbers only.'
            )

        return tfn
    
    # Allows Staff to create and assign a task.
    class Meta:
        model = Task
        fields = ['title', 'description', 'assigned_to', 'due_date']

        # Adds helpful labels and input types.
        widgets = {
            'title': forms.TextInput(
                attrs={
                    'placeholder': 'Enter task title...'
                }
            ),
            'description': forms.Textarea(
                attrs={
                    'placeholder': 'Enter task description...',
                    'rows': 4
                }
            ),
            'due_date': forms.DateInput(
                attrs={
                    'type': 'date'
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        # Initialises the form.
        super().__init__(*args, **kwargs)

        # Shows only Client accounts in the assignment field.
        self.fields['assigned_to'].queryset = (
            self.fields['assigned_to'].queryset.filter(
                role='CLIENT'
            )
        )

class DocumentRequirementForm(forms.ModelForm):
    # Allows Staff to create a document requirement for a Client.
    class Meta:
        model = DocumentRequirement
        fields = ['client', 'document_name', 'description']

        # Adds helpful labels and placeholders.
        widgets = {
            'document_name': forms.TextInput(
                attrs={
                    'placeholder': 'e.g. Bank Statement'
                }
            ),
            'description': forms.Textarea(
                attrs={
                    'placeholder': 'Enter instructions for the Client...',
                    'rows': 4
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        # Initialises the form.
        super().__init__(*args, **kwargs)

        # Shows only Client accounts in the Client field.
        self.fields['client'].queryset = (
            self.fields['client'].queryset.filter(
                role='CLIENT'
            )
        )

class TaxReturnForm(forms.ModelForm):
    # Allows Clients to provide their tax return information.

    def clean_tfn(self):
        # Gets the TFN entered by the Client.
        tfn = self.cleaned_data.get('tfn')

        # Makes sure the TFN contains numbers only.
        if tfn and not tfn.isdigit():
            raise forms.ValidationError(
                'TFN must contain numbers only.'
            )
        
        # Makes sure the TFN contains exactly 9 digits.
        if tfn and len(tfn) != 9:
            raise forms.ValidationError(
                'TFN must contain exactly 9 digits.'
            )
        return tfn

    def clean_abn(self):
        # Gets the ABN entered by the Client.
        abn = self.cleaned_data.get('abn')

        # ABN is optional, so an empty value is allowed.
        if not abn:
            return abn

        # Makes sure the ABN contains numbers only.
        if not abn.isdigit():
            raise forms.ValidationError(
                'ABN must contain numbers only.'
            )

        # Makes sure the ABN contains exactly 11 digits.
        if len(abn) != 11:
            raise forms.ValidationError(
                'ABN must contain exactly 11 digits.'
            )

        return abn

    def clean_financial_year(self):
        # Gets the Financial Year entered by the Client.
        financial_year = self.cleaned_data.get('financial_year')

        # Checks that the Financial Year follows the format 2025-26.
        import re

        if financial_year and not re.fullmatch(
            r'\d{4}-\d{2}',
            financial_year
        ):
            raise forms.ValidationError(
                'Financial Year must use the format YYYY-YY, for example 2025-26.'
            )

        return financial_year

    class Meta:
        model = TaxReturn
        fields = [
            'financial_year',
            'tfn',
            'abn',
            'address',
            'total_income',
            'tax_withheld',
            'deductions',
            'client_notes'
        ]

        labels = {
            'financial_year': 'Financial Year',
            'tfn': 'Tax File Number (TFN)',
            'abn': 'Australian Business Number (ABN) - Optional',
            'address': 'Address',
            'total_income': 'Total Income',
            'tax_withheld': 'Tax Withheld',
            'deductions': 'Deductions',
            'client_notes': 'Additional Notes',
        }

        widgets = {
            'financial_year': forms.TextInput(
                attrs={
                    'placeholder': 'e.g. 2025-26'
                }
            ),

            'tfn': forms.TextInput(
                attrs={
                    'placeholder': 'Enter your TFN'
                }
            ),

            'abn': forms.TextInput(
                attrs={
                    'placeholder': 'Enter your ABN if applicable'
                }
            ),

            'address': forms.Textarea(
                attrs={
                    'placeholder': 'Enter your residential or mailing address',
                    'rows': 3
                }
            ),

            'total_income': forms.NumberInput(
                attrs={
                    'placeholder': 'Enter total income',
                    'step': '0.01'
                }
            ),

            'tax_withheld': forms.NumberInput(
                attrs={
                    'placeholder': 'Enter tax withheld',
                    'step': '0.01'
                }
            ),

            'deductions': forms.NumberInput(
                attrs={
                    'placeholder': 'Enter total deductions',
                    'step': '0.01'
                }
            ),

            'client_notes': forms.Textarea(
                attrs={
                    'placeholder': 'Add any additional information for Staff...',
                    'rows': 4
                }
            ),
        }

class StaffTaxReturnReviewForm(forms.ModelForm):
    # Allows Staff to enter the estimated tax outcome and review notes.
    class Meta:
        model = TaxReturn
        fields = [
            'estimated_refund',
            'estimated_amount_payable',
            'staff_notes'
        ]
        labels = {
            'estimated_refund': 'Estimated Tax Refund ($)',
            'estimated_amount_payable': 'Estimated Amount Payable ($)',
            'staff_notes': 'Staff Notes',
        }
        widgets = {
            'estimated_refund': forms.NumberInput(attrs={
                'placeholder': 'Enter estimated refund',
                'step': '0.01'
            }),
            'estimated_amount_payable': forms.NumberInput(attrs={
                'placeholder': 'Enter estimated amount payable',
                'step': '0.01'
            }),
            'staff_notes': forms.Textarea(attrs={
                'placeholder': 'Enter review notes for the Client...',
                'rows': 4
            }),
        }