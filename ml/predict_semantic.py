import joblib
from sentence_transformers import SentenceTransformer


# Load semantic embedding model
embedding_model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)

# Load trained classifier
classifier = joblib.load(
    "ml/semantic_question_classifier.pkl"
)


def predict_question(question):

    # Convert question into semantic embedding
    embedding = embedding_model.encode(
        [question],
        normalize_embeddings=True
    )

    # Predict category
    prediction = classifier.predict(
        embedding
    )[0]

    # Calculate confidence
    probabilities = classifier.predict_proba(
        embedding
    )[0]

    confidence = max(probabilities) * 100

    return {
        "category": prediction,
        "confidence": round(confidence, 2)
    }


# Test questions
if __name__ == "__main__":

    print("\n================================")
    print("IP-SAKTI SAHAYAK SEMANTIC ML")
    print("================================")
    print("Type 'exit' to stop.\n")

    while True:

        question = input("Ask your question: ")

        if question.lower().strip() == "exit":
            break

        result = predict_question(question)

        print("\nCategory:", result["category"])
        print("Confidence:", result["confidence"], "%")
        print()