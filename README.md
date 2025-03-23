# SmartExpenseTracker

**SmartExpenseTracker** is a web application built with Django that helps users manage and track their income, expenses, and budget. Users can add, edit, and view their transactions while keeping track of their financial goals and limits.

## Features

- **User Authentication**: Register, login, and manage account details.
- **Income & Expense Tracking**: Record income and expenses, link them to categories and payment methods.
- **Category Management**: Create and manage custom categories for income and expenses.
- **Budget Management**: Set and track budgets for each category.
- **Profile Management**: Update personal details and upload a profile picture.
- **Transactions**: View a history of all transactions, with options for filtering by category, month, or year.
- **Responsive Design**: Mobile-friendly user interface.

- ## Installation

### Prerequisites

- Python 3.x
- Django 3.x or later
- PostgreSQL (if you plan to switch from SQLite to PostgreSQL)
- Virtual environment (recommended)

- ### Setup Instructions

1. Clone the repository:
   ```bash
   git clone https://github.com/shyamsndr/SmartExpenseTracker.git
2. Navigate to the project folder:
   cd SmartExpenseTracker
3. Create and activate a virtual environment:
   python -m venv venv
   source venv/bin/activate  # On Linux/macOS
   venv\Scripts\activate  # On Windows
4. Install dependencies:
   pip install -r requirements.txt
5. Run migrations to set up the database:
   python manage.py migrate
6. Create a superuser for accessing the admin panel:
   python manage.py createsuperuser
7. Start the development server:
   python manage.py runserver
8. Access the application at http://127.0.0.1:8000/.
