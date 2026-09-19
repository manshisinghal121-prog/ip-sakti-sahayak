import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
from sklearn.calibration import CalibratedClassifierCV
from sklearn.metrics import accuracy_score, classification_report


# Load dataset
data = pd.read_csv("ml/dataset.csv")

X = data["text"]
y = data["label"]


# Train-test split
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)


# Linear SVM with probability calibration
svm = LinearSVC(
    class_weight="balanced",
    random_state=42
)

calibrated_svm = CalibratedClassifierCV(
    svm,
    cv=5
)


model = Pipeline([
    ("tfidf", TfidfVectorizer(
        lowercase=True,
        ngram_range=(1, 2),
        sublinear_tf=True
    )),
    ("classifier", calibrated_svm)
])


# Train
model.fit(X_train, y_train)


# Evaluate
predictions = model.predict(X_test)

accuracy = accuracy_score(y_test, predictions)

print("\n========================================")
print("FINAL LINEAR SVM MODEL")
print("========================================")

print("\nAccuracy:", round(accuracy * 100, 2), "%")

print("\nClassification Report:")
print(
    classification_report(
        y_test,
        predictions
    )
)


# Save final model
joblib.dump(
    model,
    "ml/question_classifier.pkl"
)

print("\nFinal SVM model saved successfully!")
print("Location: ml/question_classifier.pkl")