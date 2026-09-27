import joblib
from pathlib import Path


# --------------------------------------------------
# MODEL PATH
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent

MODEL_PATH = BASE_DIR / "question_classifier.pkl"

model = joblib.load(MODEL_PATH)


# --------------------------------------------------
# HERB / GENERAL INFORMATION KEYWORDS
# --------------------------------------------------

HERB_KEYWORDS = [
    "ashwagandha",
    "asparagus",
    "brahmi",
    "tulsi",
    "holy basil",
    "turmeric",
    "haldi",
    "neem",
    "amla",
    "giloy",
    "ginger",
    "adrak",
    "haritaki",
    "harad",
    "bibhitaki",
    "baheda",
    "shatavari",
    "mulethi",
    "licorice",
    "aloe vera",
    "aloe",
    "arjuna",
    "jatamansi",
    "sarpagandha",
    "guduchi",
    "punarnava",
    "moringa",
    "cinnamon",
    "dalchini",
    "clove",
    "laung",
    "cardamom",
    "elaichi",
    "black pepper",
    "pepper",
]


HERB_INFORMATION_PHRASES = [
    "tell me about",
    "what is",
    "what are the benefits",
    "benefits of",
    "uses of",
    "use of",
    "properties of",
    "information about",
    "explain",
    "describe",
    "how is it used",
    "what does it do",
]


# --------------------------------------------------
# PREDICTION FUNCTION
# --------------------------------------------------

def predict_question(question):

    question = str(question).strip()

    if not question:
        return {
            "category": "General Information",
            "confidence": 0.0,
            "confidence_level": "Low"
        }

    question_lower = question.lower()


    # --------------------------------------------------
    # 1. CHECK FOR HERB INFORMATION QUESTIONS
    # --------------------------------------------------

    contains_herb = any(
        keyword in question_lower
        for keyword in HERB_KEYWORDS
    )

    contains_information_phrase = any(
        phrase in question_lower
        for phrase in HERB_INFORMATION_PHRASES
    )


    # If the user is clearly asking general information
    # about an herb then don't let the ML model route it
    # incorrectly to a regulatory category.

    if contains_herb and contains_information_phrase:

        return {
            "category": "Herb Information",
            "confidence": 95.0,
            "confidence_level": "High"
        }


    # --------------------------------------------------
    # 2. USE ML MODEL FOR OTHER QUESTIONS
    # --------------------------------------------------

    prediction = model.predict([question])[0]

    probabilities = model.predict_proba([question])[0]

    confidence = max(probabilities)

    confidence_percent = round(
        float(confidence) * 100,
        2
    )


    # --------------------------------------------------
    # 3. CONFIDENCE LEVEL
    # --------------------------------------------------

    if confidence_percent >= 80:

        confidence_level = "High"

    elif confidence_percent >= 60:

        confidence_level = "Medium"

    else:

        confidence_level = "Low"


    # --------------------------------------------------
    # 4. RETURN RESULT
    # --------------------------------------------------

    return {
        "category": str(prediction),
        "confidence": confidence_percent,
        "confidence_level": confidence_level
    }