import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC
from sklearn.metrics import accuracy_score, classification_report


# Load dataset
data = pd.read_csv("ml/dataset.csv")

X = data["text"]
y = data["label"]


# SAME test split for both models
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)


# ==================================================
# MODEL 1 — LOGISTIC REGRESSION
# ==================================================

logistic_model = Pipeline([
    ("tfidf", TfidfVectorizer(
        lowercase=True,
        ngram_range=(1, 2),
        sublinear_tf=True
    )),
    ("classifier", LogisticRegression(
        max_iter=2000,
        class_weight="balanced"
    ))
])

logistic_model.fit(X_train, y_train)

logistic_predictions = logistic_model.predict(X_test)

logistic_accuracy = accuracy_score(
    y_test,
    logistic_predictions
)


# ==================================================
# MODEL 2 — LINEAR SVM
# ==================================================

svm_model = Pipeline([
    ("tfidf", TfidfVectorizer(
        lowercase=True,
        ngram_range=(1, 2),
        sublinear_tf=True
    )),
    ("classifier", LinearSVC(
        class_weight="balanced",
        random_state=42
    ))
])

svm_model.fit(X_train, y_train)

svm_predictions = svm_model.predict(X_test)

svm_accuracy = accuracy_score(
    y_test,
    svm_predictions
)


# ==================================================
# RESULTS
# ==================================================

print("\n========================================")
print("MODEL COMPARISON")
print("========================================")

print("\nLogistic Regression Accuracy:")
print(round(logistic_accuracy * 100, 2), "%")

print("\nLinear SVM Accuracy:")
print(round(svm_accuracy * 100, 2), "%")


print("\n========================================")
print("LOGISTIC REGRESSION REPORT")
print("========================================")

print(
    classification_report(
        y_test,
        logistic_predictions
    )
)


print("\n========================================")
print("LINEAR SVM REPORT")
print("========================================")

print(
    classification_report(
        y_test,
        svm_predictions
    )
)


print("\n========================================")
print("COMPARISON COMPLETE")
print("========================================")