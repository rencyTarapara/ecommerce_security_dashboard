# E-Commerce Security Dashboard

An interactive and secure dashboard to monitor user activity and detect threats in an e-commerce system. Built with **Python** and **Streamlit**, using ML models for fraud, bot, and behaviour detection.

## Features

- 🔐 User registration & login with bcrypt-style hashed passwords (Werkzeug)
- 🛍️ User dashboard: shopping cart, order placement, ML-based anomaly detection
- 🛠️ Admin dashboard: multi-model analysis of uploaded CSV data
- 📧 Email confirmation on registration and orders (Gmail SMTP)
- 🤖 ML models: Fraud Detection, Bot Detection, Behaviour Anomaly, Security Threat

## Project Structure

```
ecommerce_security_dashboard/
├── app.py                    # Main entry point
├── pages/
│   ├── 2_Login.py
│   ├── 3_Register.py
│   ├── 4_User_Dashboard.py
│   └── 5_Admin_Dashboard.py
├── utils/
│   ├── __init__.py
│   ├── auth.py               # Login, registration, password hashing
│   └── fraud_model.py        # Fraud prediction helper
├── model/                    # Trained .pkl model files (not committed to Git)
├── data/
│   ├── users.csv             # Registered users (hashed passwords)
│   ├── admin.csv             # Admin accounts (hashed passwords)
│   ├── purchase_history.csv  # Order history
│   └── live_predictions.csv  # Real-time session predictions (auto-generated)
├── tests/
│   └── test_auth.py          # Unit tests for auth utility
├── .streamlit/
│   ├── config.toml           # Streamlit theme & server config
│   └── secrets.toml.example  # Template — copy to secrets.toml (never commit secrets!)
├── requirements.txt
└── README.md
```

## Local Setup

```bash
git clone https://github.com/rencyTarapara/ecommerce_security_dashboard.git
cd ecommerce_security_dashboard

# Install dependencies
pip install -r requirements.txt

# Configure secrets (email)
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
# Edit .streamlit/secrets.toml and fill in your Gmail credentials

# Run the app
streamlit run app.py
```

## Secrets Configuration

Copy `.streamlit/secrets.toml.example` to `.streamlit/secrets.toml` and fill in:

```toml
[EMAIL]
sender = "your-email@gmail.com"
app_password = "your-gmail-app-password"
```
> **Never** commit `secrets.toml` — it is listed in `.gitignore`.

## Deploying to Streamlit Community Cloud

1. Push the repository to GitHub (model `.pkl` files are NOT committed — host them on Git LFS or include a model-training script).
2. In Streamlit Cloud, add your secrets under **App Settings → Secrets** using the same `[EMAIL]` structure.
3. Set the main file to `app.py`.
4. Click **Deploy**.

> ⚠️ Model `.pkl` files are excluded by `.gitignore`. Before deploying, either:
> - Use [Git LFS](https://git-lfs.github.com/) to track `.pkl` files, **or**
> - Add a `setup.sh` or startup script that regenerates models from the training scripts in `utils/`.

## Running Tests

```bash
pytest tests/test_auth.py -v
```

All 10 auth tests should pass.

## Security Notes

- Passwords are hashed using `werkzeug.security.generate_password_hash` (scrypt by default).
- Role-based access control prevents users from accessing the admin dashboard.
- Email secrets are loaded from Streamlit secrets, never hardcoded.
