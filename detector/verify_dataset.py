import pandas as pd

def verify_dataset():
    df = pd.read_csv("datasets/features.csv")

    print(f"Shape: {df.shape}")

    print("\nClass distribution:")
    print(df["label"].value_counts())

    print("\nMissing values:")
    print(df.isnull().sum())

    print("\nInfinite values:")
    print(
        df.replace(
            [float("inf"), float("-inf")],
            pd.NA
        ).isna().sum()
    )

if __name__ == "__main__":
    verify_dataset()
