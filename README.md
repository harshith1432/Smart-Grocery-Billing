# Smart Grocery Billing & POS System

A modern, full-stack Grocery Store Billing and Point-of-Sale (POS) System built with Python, Flask, Neon PostgreSQL, and Bootstrap 5. This system simplifies inventory management for managers and accelerates the checkout process for cashiers with a dynamic, real-time cart and automatic invoice generation.

## 🌟 Key Features

### 1. Manager Dashboard
- **Secure Authentication**: Manager login system utilizing `bcrypt` password hashing.
- **Inventory Management**: Full CRUD (Create, Read, Update, Delete) capabilities for store products.
- **Product Details**: Supports barcode tracking, dynamic pricing types (Per Item, Per Kg, Per Gram), and variable GST percentage configurations.
- **Analytics & Alerts**: View total products, track daily sales totals, and receive low-stock alerts visually directly from the dashboard.
- **Seamless UI**: Built with Bootstrap 5 modals and AJAX for smooth, no-refresh operations.

### 2. Cashier Billing Module
- **Speedy Checkout**: Rapidly search and add products using Barcode scanning or Product IDs.
- **Dynamic Cart**: Real-time Javascript calculation of Subtotals, individual Item GST computations, and dynamic Grand Totals.
- **Flexible Management**: Editable quantities and ability to quickly remove items from the live cart.
- **Checkout Processing**: Apply dynamic discounts and choose from multiple payment methods (Cash, Card, UPI).

### 3. Automated Invoice Generation
- **Print-Ready Design**: Generates a clean, itemized HTML receipt optimized for printing and PDF saving.
- **Details**: Displays Store details, GSTIN, time of transaction, complete itemized breakdown (Subtotal, GST, Discount), and Grand Total.

## 💻 Tech Stack
- **Backend Framework**: Python Flask
- **Database**: PostgreSQL (Hosted on Neon DB)
- **ORM**: Flask-SQLAlchemy
- **Frontend**: HTML5, Vanilla JavaScript, CSS3, Bootstrap 5 (Responsive UI)
- **Security**: Flask-Bcrypt (Password Hashing)

## 🚀 Installation & Setup

### Prerequisites
- Python 3.8+ installed on your machine.
- Pip package manager.

### 1. Clone the Repository
```bash
git clone https://github.com/harshith1432/Smart-Grocery-Billing.git
cd Smart-Grocery-Billing
```

### 2. Install Dependencies
This project uses global dependencies. Install the required Python packages directly:
```bash
pip install Flask Flask-SQLAlchemy psycopg2-binary bcrypt Flask-Bcrypt python-dotenv
```

### 3. Environment Configuration
Create a `.env` file in the root directory and add the following context (the provided connection string points to your Neon PostgreSQL instance):
```env
FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=super-secret-grocery-key-123
DATABASE_URL=postgresql://neondb_owner:npg_S37kKgqUtGmf@ep-steep-king-aivy1dau-pooler.c-4.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require
```

### 4. Run the Application
Start the Flask server:
```bash
python app.py
```

*The application will ensure the database tables are created automatically and will seed a default Manager account if it doesn't exist.*

## 📖 Usage Guide

1. Navigate to `http://127.0.0.1:5000/`. You will be automatically redirected to the Login page.
2. Sign in with the default manager credentials:
   - **Username**: `admin`
   - **Password**: `admin123`
3. Upon logging in, you will be routed to the **Billing Dashboard**.
4. To add or manage inventory, click the **Manager Dashboard** link in the top navigation bar.
5. In the Manager Dashboard, try adding new items using the "Add Product" button.
6. Return to the Billing section, search for your new products by ID or Barcode, adjust quantities, apply a discount, and click "Generate Bill & Print".
7. Save the resulting pop-up dialogue safely as a PDF Invoice.

## 📜 License
This project is for educational purposes. Feel free to modify and expand!
