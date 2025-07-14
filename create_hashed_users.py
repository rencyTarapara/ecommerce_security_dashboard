import pandas as pd
from werkzeug.security import generate_password_hash

data = {
    "username": ["admin", "testuser"],
    "password": [generate_password_hash("admin123"), generate_password_hash("user123")],
    "role": ["admin", "user"],
    "phone": ["9510733252", "8888888888"]  # Replace with valid dummy or real numbers
}

df = pd.DataFrame(data)
df.to_csv("data/users.csv", index=False)
