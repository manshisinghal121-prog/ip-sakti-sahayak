import pandas as pd

original = pd.read_csv("ml/dataset.csv")
augmented = pd.read_csv("ml/ip_sakti_semantic_augmented_examples.csv")

combined = pd.concat(
    [original[["text", "label"]], augmented[["text", "label"]]],
    ignore_index=True
)

# Remove exact duplicates
combined = combined.drop_duplicates(
    subset=["text", "label"]
).reset_index(drop=True)

combined.to_csv(
    "ml/semantic_training_dataset.csv",
    index=False
)

print("Original examples:", len(original))
print("New examples:", len(augmented))
print("Combined examples:", len(combined))

print("\nCategory distribution:")
print(combined["label"].value_counts())