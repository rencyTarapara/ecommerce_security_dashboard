# ecommerce_security_dashboard

An interactive and secure dashboard designed to monitor user activity and detect threats in an e-commerce system. Built using **Python** and **Streamlit**, this project uses **CSV files as the database** for logging and analysis.

## Project Structure
ecommerce_security_dashboard/
│
├── data/ # CSV files (users, logs, threats)
├── model/ # ML or rule-based detection models
├── pages/ # Streamlit multipage components
├── utils/ # Helper and utility functions
│
├── .gitignore # Git ignore rules
├── README.md # Project documentation
├── app.py # Main dashboard script
├── create_hashed_users.py # Script for generating secure user hashes
├── .secret/ secrets.toml # Local config (local database .csv)

## Features

-  User login system with hashed passwords
-  Visual dashboard for activity & threat monitoring
-  CSV-based data storage (easy to manage and portable)
-  Basic machine learning model support
-  Modular codebase for easy enhancements


'''bash
git clone https://github.com/renshiTarapara/ecommerce_security_dashboard.git
cd ecommerce_security_dashboard


