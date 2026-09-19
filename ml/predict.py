import joblib

# Load final trained model
model = joblib.load("ml/question_classifier.pkl")


def predict_question(question):

    prediction = model.predict([question])[0]

    probabilities = model.predict_proba([question])[0]

    confidence = max(probabilities)

    confidence_percent = round(
        float(confidence) * 100,
        2
    )

    # ---------------------------------------------------------
    # LOW-CONFIDENCE HANDLING
    # Keep the ML prediction instead of replacing it with
    # "Needs More Information".
    # ---------------------------------------------------------

    if confidence < 0.35:
        category = prediction
        confidence_level = "Very Low"

    elif confidence < 0.50:
        category = prediction
        confidence_level = "Low"

    elif confidence < 0.70:
        category = prediction
        confidence_level = "Moderate"

    else:
        category = prediction
        confidence_level = "High"

    return {
        "category": category,
        "confidence": confidence_percent,
        "confidence_level": confidence_level
    }


if __name__ == "__main__":

    question = input("Enter your question: ")

    result = predict_question(question)

    print("\nCategory:", result["category"])
    print("Confidence:", result["confidence"], "%")
    print("Confidence Level:", result["confidence_level"])