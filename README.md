# Finfy - AI-Driven Loan Eligibility App (Under-development)

<p align="center">
  <img src="https://github.com/user-attachments/assets/8021a279-1fcc-4fcb-9215-dfe11dace72b" alt="Logo" width="300">
</p>

Finfy is an AI-powered interface that checks the loan eligibility using machine learning. It aims to enhance.

## 🏗️ Tech Stack
- **Frontend**: HTML, CSS, Bootstrap (for UI/UX)
- **Backend**: Flask (Python-based web framework)
- **Database**: SQLite for development
- **Machine Learning**: Scikit-learn (for credit risk prediction)
- **Deployment**: Heroku / AWS (Still not deployed)

## 🔧 Installation & Setup

1. **Clone the Repository**
   ```sh
   git clone https://github.com/eatulrajput/finfy-app.git
   cd loan_approval
   ```
2. **Create a Virtual Environment**
   ```sh
   python3 -m venv venv
   source venv/bin/activate  # For macOS/Linux
   venv\Scripts\activate  # For Windows
   ```
3. **Install Dependencies**
   ```sh
   pip install -r requirements.txt
   ```
4. **Apply Migrations**
   ```sh
   python manage.py migrate
   ```
5. **Run the Server**
   ```sh
   python manage.py runserver
   ```

## 📌 Usage
1. Register/Login as a user.
2. Apply for a loan by filling in the required details.
3. View loan status and check creditworthiness predictions.
4. Fund available loans if you're a lender.
5. Loan approval and repayment handled through the platform.

## 🤖 Machine Learning Models
- **Logistic Regression**: Predicts loan approval probability.

## 🚀 Future Enhancements
- **UPI-based Transactions**: Enable seamless funding and repayments.
- **Live Credit Score Updates**: Real-time creditworthiness tracking.
- **Blockchain Integration**: Secure and transparent loan transactions.

## 🛠️ Contributing
Want to contribute? Follow these steps:
1. Fork the repo
2. Create a new branch (`git checkout -b feature-branch`)
3. Commit changes (`git commit -m 'Add new feature'`)
4. Push to the branch (`git push origin feature-branch`)
5. Create a pull request

## 📜 License
This project is licensed under the **MIT License**.

## 🙌 Acknowledgments
Special thanks to the contributors and open-source community for making this project possible!

---
**Made with ❤️ by the Finfy Team**

