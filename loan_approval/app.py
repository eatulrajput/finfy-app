import os
import pickle
import pandas as pd
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Replace with a secure key!

# Configure SQLite database
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'users.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ---------------------------
# Database Models
# ---------------------------
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    is_blocked = db.Column(db.Boolean, default=False)

class LoanRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    borrower_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    lender_username = db.Column(db.String(150), nullable=False)
    userGender = db.Column(db.String(50))              # Gender
    maritalStatus = db.Column(db.String(50))        # Marital Status
    dependentsNo = db.Column(db.String(50))         # Dependents
    educationLevel = db.Column(db.String(50))            # Education
    employeeStatus = db.Column(db.String(50))           # Employed
    userIncome = db.Column(db.Float)                    # Income
    spouseIncome = db.Column(db.Float)            # Spouse's Income
    loanAmount = db.Column(db.Float)               # Loan Amount
    loanInstallment = db.Column(db.Float)         # Monthly Installment
    creditHistory = db.Column(db.Float)        # Credit History
    propertyStatus = db.Column(db.String(50))              # Property
    status = db.Column(db.String(50), default="pending")  # pending, accepted, rejected, withdrawn

    # Relationship to User model
    borrower = db.relationship('User', backref=db.backref('loan_requests', lazy=True))

# Create the database tables within the app context
with app.app_context():
    db.create_all()

# Load the pre-trained loan prediction model, scaler, and feature order
with open("model.pkl", "rb") as file:
    model = pickle.load(file)
with open("scaler.pkl", "rb") as file:
    scaler = pickle.load(file)
with open("columns_order.pkl", "rb") as file:
    columns_order = pickle.load(file)

# -------------------------
# Helper Functions
# -------------------------
def admin_required():
    # Check if current user is admin
    if 'user' not in session:
        return False
    user = User.query.filter_by(username=session['user']).first()
    return user and user.is_admin

# -------------------------
# Routes for the Website
# -------------------------

@app.route('/')
def index():
    return render_template('index.html')

# Registration route (only one definition)
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        admin_code = request.form.get('admin_code', '').strip()  # New field for admin code
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists! Try a different one.')
            return redirect(url_for('register'))
        
        hashed_password = generate_password_hash(password)
        # If the admin code matches your secret (change 'success2426' to your desired secret)
        is_admin = True if admin_code == 'success2426' else False
        
        new_user = User(username=username, password=hashed_password, is_admin=is_admin)
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful! Please log in.')
        return redirect(url_for('login'))
    return render_template('register.html')

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user:
            if user.is_blocked:
                flash('This account is blocked. Please contact support.')
                return redirect(url_for('login'))
            if check_password_hash(user.password, password):
                session['user'] = user.username
                return redirect(url_for('dashboard'))
        flash('Invalid username or password!')
        return redirect(url_for('login'))
    return render_template('login.html')

# Logout route
@app.route('/logout')
def logout():
    session.pop('user', None)
    flash('Logged out successfully!')
    return redirect(url_for('index'))

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'user' not in session:
        flash('Please log in to access the dashboard!')
        return redirect(url_for('login'))

    prediction_text = ""

    if request.method == 'POST' and "eligibility" in request.form:
        # Process the eligibility checker form
        data = request.form.to_dict()
        input_df = pd.DataFrame([data])
        numeric_cols = ['dependentsNo', 'userIncome', 'spouseIncome', 'loanAmount', 'loanInstallment', 'creditHistory']
        for col in numeric_cols:
            if col in input_df.columns:
                input_df[col] = pd.to_numeric(input_df[col], errors='coerce')
        input_df = input_df.fillna(0)
        input_processed = pd.get_dummies(input_df, drop_first=True)
        input_processed = input_processed.reindex(columns=columns_order, fill_value=0)
        input_scaled = scaler.transform(input_processed)
        prediction = model.predict(input_scaled)
        prediction_text = "Eligible for Loan" if prediction[0] == 1 else "Not Eligible for Loan"

    user = User.query.filter_by(username=session['user']).first()

    # Loan requests where the logged in user is the lender
    lender_requests = LoanRequest.query.filter_by(lender_username=session['user']).all()

    # Loan requests made by the logged-in user (as borrower)
    borrower_requests = LoanRequest.query.filter_by(borrower_id=user.id).all()

    # 🔍 Debugging: Print borrower details to check if data is available
    print("\n🔎 Checking Loan Requests Data:")
    for req in lender_requests:
        print(f"📌 Borrower: {req.borrower.username}")
        print(f"🧑 Gender: {req.userGender}")
        print(f"💰 Income: {req.userIncome}")
        print(f"🏠 Property Status: {req.propertyStatus}")
        print("--------------------------------------------------")


    return render_template('dashboard.html', prediction_text=prediction_text,
                           lender_requests=lender_requests, borrower_requests=borrower_requests)

# Route for a user to request a loan from another user
@app.route('/request_loan', methods=['GET', 'POST'])
def request_loan():
    if 'user' not in session:
        flash('Please log in to request a loan!')
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        lender_username = request.form['lender_username']
        new_request = LoanRequest(
            borrower_id = User.query.filter_by(username=session['user']).first().id,
            lender_username = lender_username,
            userGender = request.form['userGender'],
            maritalStatus = request.form['maritalStatus'],
            dependentsNo = request.form['dependentsNo'],
            educationLevel = request.form['educationLevel'],
            employeeStatus = request.form['employeeStatus'],
            userIncome = float(request.form['userIncome']),
            spouseIncome = float(request.form['spouseIncome']),
            loanAmount = float(request.form['loanAmount']),
            loanInstallment = float(request.form['loanInstallment']),
            creditHistory = float(request.form['creditHistory']),
            propertyStatus = request.form['propertyStatus']
        )
        db.session.add(new_request)
        db.session.commit()
        flash('Loan request submitted successfully!')
        return redirect(url_for('dashboard'))
    
    return render_template('request_loan.html')

# Endpoint for lender to reject a loan request (delete the record)
@app.route('/reject_loan/<int:loan_id>', methods=['POST'])
def reject_loan(loan_id):
    if 'user' not in session:
        flash('Please log in!')
        return redirect(url_for('login'))
    loan_request = LoanRequest.query.get(loan_id)
    if loan_request and loan_request.lender_username == session['user']:
        db.session.delete(loan_request)
        db.session.commit()
        flash('Loan request rejected and removed successfully!')
    else:
        flash('Not authorized to reject this loan request.')
    return redirect(url_for('dashboard'))

# Endpoint for lender to accept a loan request (update status to accepted)
@app.route('/accept_loan/<int:loan_id>', methods=['POST'])
def accept_loan(loan_id):
    if 'user' not in session:
        flash('Please log in!')
        return redirect(url_for('login'))
    loan_request = LoanRequest.query.get(loan_id)
    if loan_request and loan_request.lender_username == session['user']:
        loan_request.status = 'accepted'
        db.session.commit()
        flash('Loan request accepted successfully!')
    else:
        flash('Not authorized to accept this loan request.')
    return redirect(url_for('dashboard'))

# Endpoint for borrower to withdraw their loan request
@app.route('/withdraw_loan/<int:loan_id>', methods=['POST'])
def withdraw_loan(loan_id):
    if 'user' not in session:
        flash('Please log in!')
        return redirect(url_for('login'))
    user = User.query.filter_by(username=session['user']).first()
    loan_request = LoanRequest.query.get(loan_id)
    if loan_request and loan_request.borrower_id == user.id:
        loan_request.status = 'withdrawn'
        db.session.commit()
        flash('Loan request withdrawn successfully!')
    else:
        flash('Not authorized to withdraw this loan request.')
    return redirect(url_for('dashboard'))

# -------------------------
# Admin Routes
# -------------------------

@app.route('/admin')
def admin_dashboard():
    if not admin_required():
        flash('Admin access required!')
        return redirect(url_for('dashboard'))
    return render_template('admin_dashboard.html')

@app.route('/admin/users')
def admin_users():
    if not admin_required():
        flash('Admin access required!')
        return redirect(url_for('dashboard'))
    users = User.query.all()
    return render_template('admin_users.html', users=users)

@app.route('/admin/loans')
def admin_loans():
    if not admin_required():
        flash('Admin access required!')
        return redirect(url_for('dashboard'))
    loans = LoanRequest.query.all()
    return render_template('admin_loans.html', loans=loans)

@app.route('/admin/block_user/<int:user_id>', methods=['POST'])
def admin_block_user(user_id):
    if not admin_required():
        flash('Admin access required!')
        return redirect(url_for('dashboard'))
    user = User.query.get(user_id)
    if user:
        user.is_blocked = True
        db.session.commit()
        flash(f'User {user.username} has been blocked.')
    else:
        flash('User not found.')
    return redirect(url_for('admin_users'))

@app.route('/admin/unblock_user/<int:user_id>', methods=['POST'])
def admin_unblock_user(user_id):
    if not admin_required():
        flash('Admin access required!')
        return redirect(url_for('dashboard'))
    user = User.query.get(user_id)
    if user:
        user.is_blocked = False
        db.session.commit()
        flash(f'User {user.username} has been unblocked.')
    else:
        flash('User not found.')
    return redirect(url_for('admin_users'))

if __name__ == '__main__':
    app.run(debug=True)
### http://localhost:5000/admin
