import pandas as pd
import joblib

from sentence_transformers import SentenceTransformer
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix
)

# ---------------------------------------
# 1. Load dataset
# ---------------------------------------

data = pd.read_csv("ml/dataset.csv")

X = data["text"].astype(str)
y = data["label"]

print("Dataset size:", len(data))
print("\nCategory distribution:")
print(y.value_counts())


# ---------------------------------------
# 2. Train-test split
# ---------------------------------------

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)


# ---------------------------------------
# 3. Load semantic embedding model
# ---------------------------------------

print("\nLoading Sentence Transformer...")

embedding_model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)


# ---------------------------------------
# 4. Convert questions into embeddings
# ---------------------------------------

print("Creating semantic embeddings...")

X_train_embeddings = embedding_model.encode(
    X_train.tolist(),
    normalize_embeddings=True,
    show_progress_bar=True
)

X_test_embeddings = embedding_model.encode(
    X_test.tolist(),
    normalize_embeddings=True,
    show_progress_bar=True
)


# ---------------------------------------
# 5. Train classifier
# ---------------------------------------

classifier = LogisticRegression(
    max_iter=2000,
    class_weight="balanced"
)

classifier.fit(
    X_train_embeddings,
    y_train
)


# ---------------------------------------
# 6. Evaluate
# ---------------------------------------

predictions = classifier.predict(X_test_embeddings)

accuracy = accuracy_score(
    y_test,
    predictions
)

print("\n===================================")
print("SEMANTIC MODEL RESULTS")
print("===================================")

print(
    "\nAccuracy:",
    round(accuracy * 100, 2),
    "%"
)

print("\nClassification Report:")
print(
    classification_report(
        y_test,
        predictions
    )
)

print("\nConfusion Matrix:")
print(
    confusion_matrix(
        y_test,
        predictions,
        labels=classifier.classes_
    )
)


# ---------------------------------------
# 7. Save classifier
# ---------------------------------------

joblib.dump(
    classifier,
    "ml/semantic_question_classifier.pkl"
)

print(
    "\nClassifier saved:"
    " ml/semantic_question_classifier.pkl"
)