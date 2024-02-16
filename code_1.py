from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///example.db'
db = SQLAlchemy(app)

# Step 2: Define Entities
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)

class Company(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    employees = db.Column(db.Integer)
    users = db.relationship('User', backref='company', lazy=True)

class ClientUser(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime)
    deleted_at = db.Column(db.DateTime)
    active = db.Column(db.Boolean)

class Client(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)
    user = db.relationship('User', backref='client', lazy=True)
    company = db.relationship('Company', backref='client', lazy=True)

# Step 3: SQL Functions
def search_companies_by_employees_range(min_employees, max_employees):
    companies = Company.query.filter(Company.employees.between(min_employees, max_employees)).all()
    return companies

def search_clients_by_user(user_id):
    clients = Client.query.filter_by(user_id=user_id).all()
    return clients

def search_clients_by_name(name):
    clients = Client.query.filter(Client.company.has(Company.name.like(f'%{name}%'))).all()
    return clients

def get_companies_with_max_revenue():
    # Your SQL query to get companies with max revenue in its industry
    pass

# Step 4: SECURITY
# Secure the Create Client endpoint (2.3) to allow only ROLE_ADMIN users to use it
@app.route('/clients', methods=['POST'])
def create_client():
    # You would need some mechanism to authenticate the user's role
    # For demonstration purposes, let's assume there's a request header with user role
    user_role = request.headers.get('UserRole')
    if user_role != 'ROLE_ADMIN':
        return jsonify({'error': 'Access forbidden. Only ROLE_ADMIN users can use this endpoint.'}), 403
    # Your create client logic goes here
    pass

# Step 5: REGEX
# Add regex to validate emails on GET /user/profile endpoint
import re

@app.route('/user/profile', methods=['GET'])
def get_user_profile():
    # Fetch user profile from database
    user_profile = get_user_profile_from_database()  # Placeholder for fetching user profile
    # Validate email format using regex
    email = user_profile.get('email')
    if email and not re.match(r'^[\w\.-]+@[a-zA-Z\d\.-]+\.[a-zA-Z]{2,}$', email):
        return jsonify({'error': 'Invalid email format'}), 400
    return jsonify(user_profile)

# Step 6: UNIT AND/OR FUNCTIONAL TESTS
import unittest

class TestAPI(unittest.TestCase):

    def test_company_employee_count(self):
        # Test if there is only one company with more than 200000 employees
        self.assertEqual(len(Company.query.filter(Company.employees > 200000).all()), 1)

    def test_role_user_cannot_create_user(self):
        # Test if ROLE_USER cannot create a User
        response = self.client.post('/users', data={'username': 'test_user'})
        self.assertEqual(response.status_code, 403)

    def test_client_creation(self):
        # Test if a Client can be created properly
        response = self.client.post('/clients', data={'name': 'Test Client', 'email': 'test@example.com', 'phone': '1234567890'})
        self.assertEqual(response.status_code, 200)

    def test_companies_revenue(self):
        # Test that result from (3.3) contains Amazon and Google and not contains any other company from E-Commerce industry
        companies = get_companies_with_max_revenue()
        self.assertIn('Amazon', companies)
        self.assertIn('Google', companies)
        self.assertNotIn('OtherECommerceCompany', companies)

if __name__ == '__main__':
    unittest.main()
