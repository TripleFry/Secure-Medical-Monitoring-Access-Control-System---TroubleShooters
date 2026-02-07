import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import classification_report, accuracy_score
from xgboost import XGBClassifier

# Load dataset
df = pd.read_csv("realistic_patient_data.csv")

# Convert target
df['Risk Category'] = df['Risk Category'].map({
    'Normal': 0,
    'High Risk': 1
})

# Encode gender
le = LabelEncoder()
df['Gender'] = le.fit_transform(df['Gender'])

# -------- Feature Engineering --------
df['BMI'] = df['Weight (kg)'] / (df['Height (m)'] ** 2)
df['Fever'] = (df['Body Temperature'] > 37.5).astype(int)
df['Low_SpO2'] = (df['Oxygen Saturation'] < 94).astype(int)

# Features
X = df[[
    'Heart Rate',
    'Body Temperature',
    'Oxygen Saturation',
    'Age',
    'Gender',
    'Weight (kg)',
    'Height (m)',
    'Smoking',
    'Hypertension',
    'BMI',
    'Fever',
    'Low_SpO2'
]]

y = df['Risk Category']

# Split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Scale
scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)

# -------- Tuned XGBoost Model --------
model = XGBClassifier(
    n_estimators=600,
    max_depth=6,
    learning_rate=0.02,
    subsample=0.9,
    colsample_bytree=0.9,
    scale_pos_weight=1.4,
    random_state=42,
    eval_metric='logloss'
)

# Train
model.fit(X_train, y_train)

# Predict
y_pred = model.predict(X_test)

# Evaluate
print("Accuracy:", accuracy_score(y_test, y_pred))
print(classification_report(y_test, y_pred))

joblib.dump(model, "model.pkl")
joblib.dump(scaler, "scaler.pkl")

print("Model and scaler saved!")