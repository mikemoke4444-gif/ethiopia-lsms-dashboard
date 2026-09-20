
import pandas as pd

df = pd.read_csv("data/raw_dataset.csv")

print("=== DATASET SHAPE ===")
print(df.shape)

print("\n=== COLUMNS ===")
print(df.columns.tolist())

print("\n=== FIRST 5 ROWS ===")
print(df.head())

print("\n=== MISSING VALUES ===")
print(df.isnull().sum())

