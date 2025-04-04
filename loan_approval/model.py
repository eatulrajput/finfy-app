import pandas as pd
import pickle
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression

# Load dataset
df = pd.read_csv("C:\\Users\\KIIT\\Downloads\\archive\\clientes.csv")

# Define target and features
target_column = "loanApproval"  # Ensure this matches your dataset
df[target_column] = df[target_column].map({'Y': 1, 'N': 0})  # Convert to 0/1

# Handle missing values
df = df.fillna(0)

# Convert categorical variables
df = pd.get_dummies(df, drop_first=True)

# Define X and y
X = df.drop(columns=[target_column])
y = df[target_column]

# Split the dataset
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Standardize the features
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Train Logistic Regression Model
model = LogisticRegression()
model.fit(X_train_scaled, y_train)

# Save model, scaler, and feature order
with open("model.pkl", "wb") as file:
    pickle.dump(model, file)

with open("scaler.pkl", "wb") as file:
    pickle.dump(scaler, file)

with open("columns_order.pkl", "wb") as file:
    pickle.dump(list(X.columns), file)

print("Model and preprocessing objects saved successfully!")
