import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
import pickle

# 1. Create mock data: 500 patients
np.random.seed(42)
n_patients = 500

data = {
    'bmi': np.random.uniform(18, 35, n_patients),
    'age': np.random.randint(20, 60, n_patients),
    'metabolism_rate': np.random.uniform(0.8, 1.2, n_patients),
    # The target: Half-life (with some biological noise)
    'half_life': []
}

# Logic: Higher BMI + Slower metabolism = Longer half-life
for i in range(n_patients):
    base = 24 # Base for THC
    hl = base * (1 + (data['bmi'][i] - 22) * 0.05) / data['metabolism_rate'][i]
    data['half_life'].append(hl + np.random.normal(0, 2))

df = pd.DataFrame(data)

# 2. Train the Random Forest Model
X = df[['bmi', 'age', 'metabolism_rate']]
y = df['half_life']

model = RandomForestRegressor(n_estimators=100)
model.fit(X, y)

# 3. Save the "Brain" to a file
with open('drug_model.pkl', 'wb') as f:
    pickle.dump(model, f)

print("ML Model trained and saved as drug_model.pkl!")