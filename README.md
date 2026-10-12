# Tax Workflow System

## Setup and Running Instructions

This README provides the basic instructions for setting up and running the Tax Workflow System locally.

### 1. Requirements

Ensure the following software is installed:

- Python 3.x
- PostgreSQL
- Visual Studio Code (recommended)

### 2. Open the Project

Open the `tax_workflow_system` project folder in Visual Studio Code.

The main project structure is as follows:

tax_workflow_system/
├── accounts/
├── documents/
├── config/
├── media/
├── venv/
├── manage.py
├── requirements.txt
└── README.md

### 3. Activate the Virtual Environment

Open a terminal in the project folder.

On Windows, activate the existing virtual environment using:
venv\Scripts\activate


If the virtual environment does not exist, create it first:
python -m venv venv

Then activate it using the command above.

### 4. Install Required Packages

Install the Python packages required by the project:
pip install -r requirements.txt

### 5. Configure the PostgreSQL Database

The application uses PostgreSQL to store its data.

Before running the application:

1. Ensure PostgreSQL is installed and running.
2. Create the required database and database user if they do not already exist.
3. Open `config/settings.py`.
4. Check the `DATABASES` configuration and ensure the database name, username, password, host, and port match your local PostgreSQL configuration.

Do not commit or share real database passwords or other sensitive credentials.

### 6. Apply Database Migrations

Django migrations create and update the database tables required by the application.

Run the following command from the project directory:
python manage.py migrate

This applies the existing migrations for the project's applications, including accounts, documents, authentication, and other Django components.

If new model changes have been made and corresponding migration files have not yet been created, run:
python manage.py makemigrations

Then apply the migrations:
python manage.py migrate

For a normal setup using the migration files already included in the project, running `python manage.py migrate` is generally sufficient.

### 7. Create a Django Superuser

To access the Django Admin interface, create a superuser account:
python manage.py createsuperuser

Follow the terminal prompts to set the username, email address if requested, and password.

The Django Admin interface is separate from the application's Client and Staff login system.

### 8. Run the Application

Start the Django development server:
python manage.py runserver

Open the local address displayed in the terminal in a web browser. By default, this is:

`http://127.0.0.1:8000/`

Keep the terminal running while using the application.

### 9. User Accounts

The application supports two main user roles:

- **Client:** Accesses client features, including tax returns, document uploads, document requirements, tasks, and notifications.
- **Staff:** Accesses staff features, including client records, tax return reviews, document management, document filtering, tasks, and document feedback.

The Django superuser is intended for administrative access and is separate from the normal Client and Staff workflow.

To create client and staff accounts, you can access the admin page by entering your superuser details and add
suitable client and staff accounts.

### 10. Uploaded Documents

During local development, uploaded documents are stored in the project's media directory, under `media/documents`.

Use sample documents when testing the application. Avoid uploading real tax records or personal information unless appropriate authorisation and safeguards are in place.

### 11. Troubleshooting

- **Database connection error:** Ensure PostgreSQL is running and the database settings in `config/settings.py` are correct.
- **Missing package error:** Activate the virtual environment and run `pip install -r requirements.txt`.
- **Database table error:** Run `python manage.py migrate`.
- **Login issue:** Check that the correct test account and password are being used.

### 12. Important Notes

- Activate the virtual environment before running Django commands.
- PostgreSQL must be running before starting the application.
- Database configuration must match the local PostgreSQL setup.
- This project is intended for local development and academic demonstration. Additional security configuration and testing are required before production deployment.

## Quick Start

After PostgreSQL has been configured and the virtual environment is available, use:

venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver

The `createsuperuser` command is only required if a Django Admin account needs to be created.