import pandas as pd
import numpy as np

target = ['Dropout', 'Enrolled', 'Graduate']
cols = [
    "Marital status", "Application mode", "Application order", "Course", 
    "Daytime/evening attendance", "Previous qualification", "Previous qualification (grade)",
    "Nacionality", "Mother's qualification", "Father's qualification", 
    "Mother's occupation", "Father's occupation", "Admission grade", "Displaced", 
    "Educational special needs", "Debtor", "Tuition fees up to date", "Gender", 
    "Scholarship holder", "Age at enrollment", "International", "Unemployment rate", 
    "Inflation rate", "GDP", "Target"
]

np.random.seed(42)
n_rows = 1000

df = pd.DataFrame(columns=cols)
for c in cols[:-1]:
    if c in ["Previous qualification (grade)", "Admission grade"]:
        df[c] = np.random.uniform(90.0, 200.0, n_rows)
    elif c in ["Unemployment rate", "Inflation rate", "GDP"]:
        df[c] = np.random.uniform(-5.0, 15.0, n_rows)
    elif c == "Age at enrollment":
        df[c] = np.random.randint(17, 45, n_rows)
    elif c == "Application order":
        df[c] = np.random.randint(0, 6, n_rows)
    else:
        df[c] = np.random.randint(0, 20, n_rows)

df["Target"] = np.random.choice(target, n_rows)

df.to_csv("data/data.csv", sep=";", index=False)
print('Generated data.csv')
