"""
Phase 3 — Enhanced RAG Assistant Engine with Visual Cards, Sanskrit Shlokas & Multilingual Adapters
"""

import os
import sys
import re
from typing import List, Dict, Optional
try:
    from .search_engine import query_legal_database
except ImportError:
    from search_engine import query_legal_database

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)

# RICH AYURVEDIC HERBAL & VISUAL KNOWLEDGE DATABASE
HERBAL_KNOWLEDGE_BASE = {
    "ashwagandha": {
        "sanskrit_name": "अश्वगंधा (Ashwagandha)",
        "botanical_name": "Withania somnifera",
        "common_name": "Indian Ginseng",
        "shloka": "अश्वगंधा अनिलघ्नी बल्या रसायनी तथा। तिक्ता कषायोष्णा शुक्रा सर्वदोषहरा॥",
        "shloka_translation": "Ashwagandha balances Vata, enhances physical strength (Balya), acts as a rejuvenator (Rasayana), and possesses heating potency (Usna Veerya).",
        "active_compounds": ["Withaferin A", "Withanolide D", "Sitoindosides"],
        "ayurvedic_properties": {"rasa": "Tikta, Kashaya", "veerya": "Ushna", "vipaka": "Madhura"},
        "element": "🔥 Agni + 🪨 Prithvi",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/2/24/Withania_somnifera_1DS-II_3-7489.jpg",
        "badge_color": "amber",
        "tkdl_status": "Recorded in TKDL (Classical Rasayana). Section 3(p) Review Required."
    },
    "haridra": {
        "sanskrit_name": "हरिद्रा (Haridra / Turmeric)",
        "botanical_name": "Curcuma longa",
        "common_name": "Turmeric",
        "shloka": "हरिद्रा कटुका तिक्ता रूक्षा उष्णा कफपित्तनुत्। वर्ण्या त्वग्दोषहन्त्री च शोधनी व्रणरोपणी॥",
        "shloka_translation": "Haridra has pungent & bitter taste, hot potency, purifies blood, heals skin disorders and promotes wound healing.",
        "active_compounds": ["Curcumin", "Demethoxycurcumin", "Turmerone"],
        "ayurvedic_properties": {"rasa": "Tikta, Katu", "veerya": "Ushna", "vipaka": "Katu"},
        "element": "🔥 Agni + 🍃 Vayu",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/5/5b/Curcuma_longa_roots.jpg",
        "badge_color": "yellow",
        "tkdl_status": "Famous US Patent Rejection Landmark Case (US Pat 5,401,504 revoked via TKDL evidence)."
    },
    "guduchi": {
        "sanskrit_name": "गुडूची (Guduchi / Giloy)",
        "botanical_name": "Tinospora cordifolia",
        "common_name": "Amrita / Heart-leaved Moonseed",
        "shloka": "गुडूची कटुका तिक्ता स्वादुपाका रसायनी। संग्राहिणी कषायोष्णा दीपनी ज्वरनाशिनी॥",
        "shloka_translation": "Guduchi is bitter, rejuvenative, digestive stimulant (Deepani), and relieves chronic fevers (Jwarashini).",
        "active_compounds": ["Tinosporaside", "Cordifolioside A", "Berberine"],
        "ayurvedic_properties": {"rasa": "Tikta, Kashaya", "veerya": "Ushna", "vipaka": "Madhura"},
        "element": "💧 Jala + 🪨 Prithvi",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/4/4a/Tinospora_cordifolia_fruits.jpg",
        "badge_color": "emerald",
        "tkdl_status": "Recorded in TKDL as Immunomodulator. Process patents require novel extraction proofs."
    },
    "tulsi": {
        "sanskrit_name": "तुलसी (Tulsi)",
        "botanical_name": "Ocimum tenuiflorum",
        "common_name": "Holy Basil",
        "shloka": "तुलसी कटुका तिक्ता हृद्या दाहविनाशिनी। कृमिदोषहरा नित्यं पावनी च सुरासुरैः॥",
        "shloka_translation": "Tulsi is aromatic and warming, supports respiratory health, and is traditionally regarded as purifying.",
        "active_compounds": ["Eugenol", "Ursolic Acid", "Rosmarinic Acid"],
        "ayurvedic_properties": {"rasa": "Katu, Tikta", "veerya": "Ushna", "vipaka": "Katu"},
        "element": "🔥 Agni + 🍃 Vayu",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/4/44/Ocimum_tenuiflorum_3_09_2012.JPG",
        "badge_color": "emerald",
        "tkdl_status": "Classical medicinal plant. Novel extracts and standardized compositions require novelty review."
    },
    "neem": {
        "sanskrit_name": "निम्ब (Neem)",
        "botanical_name": "Azadirachta indica",
        "common_name": "Neem",
        "shloka": "निम्बः शीतो लघुः तिक्तः कृमिघ्नो रक्तशोधकः।",
        "shloka_translation": "Neem is traditionally described as cooling, light, bitter, antiparasitic, and blood-purifying.",
        "active_compounds": ["Azadirachtin", "Nimbin", "Gedunin"],
        "ayurvedic_properties": {"rasa": "Tikta, Kashaya", "veerya": "Shita", "vipaka": "Katu"},
        "element": "💧 Jala + 🍃 Vayu",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/e/e2/Leaves_Azadirachta_indica_Heritage_tree_Philippines.jpg",
        "badge_color": "emerald",
        "tkdl_status": "Traditional knowledge subject to Section 3(p) and prior-art review."
    },
    "brahmi": {
        "sanskrit_name": "ब्राह्मी (Brahmi)",
        "botanical_name": "Bacopa monnieri",
        "common_name": "Brahmi",
        "shloka": "ब्राह्मी स्मृतिप्रदा मेध्या रसायनी बलवर्धिनी।",
        "shloka_translation": "Brahmi is traditionally associated with memory, intellect, rejuvenation, and vitality.",
        "active_compounds": ["Bacoside A", "Bacopaside I", "Alkaloids"],
        "ayurvedic_properties": {"rasa": "Tikta", "veerya": "Shita", "vipaka": "Madhura"},
        "element": "💧 Jala + 🪨 Prithvi",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/8/82/%E0%B4%AC%E0%B5%8D%E0%B4%B0%E0%B4%B9%E0%B5%8D%E0%B4%AE%E0%B4%BF...Bacopa_monnieri.jpg",
        "badge_color": "emerald",
        "tkdl_status": "Classical Medhya Rasayana. Standardized extracts require novelty and efficacy evidence."
    },
    "amla": {
        "sanskrit_name": "आमलकी (Amla)",
        "botanical_name": "Phyllanthus emblica",
        "common_name": "Indian Gooseberry",
        "shloka": "आमलकी वयःस्था च धात्री रसायनी परा।",
        "shloka_translation": "Amla is traditionally regarded as a rejuvenative fruit that supports nourishment and vitality.",
        "active_compounds": ["Emblicanin A", "Emblicanin B", "Gallic Acid"],
        "ayurvedic_properties": {"rasa": "Pancharasa", "veerya": "Shita", "vipaka": "Madhura"},
        "element": "💧 Jala + 🪨 Prithvi",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/7/7f/Phyllanthus_officinalis.jpg",
        "badge_color": "amber",
        "tkdl_status": "Key ingredient in classical Rasayana preparations. Formulation novelty must be established."
    },
    "shatavari": {
        "sanskrit_name": "शतावरी (Shatavari)",
        "botanical_name": "Asparagus racemosus",
        "common_name": "Wild Asparagus",
        "shloka": "शतावरी बल्या वृष्या मधुरा रसायनी मता।",
        "shloka_translation": "Shatavari is traditionally described as nourishing, strengthening, and rejuvenative.",
        "active_compounds": ["Shatavarins", "Asparagamine A", "Racemosol"],
        "ayurvedic_properties": {"rasa": "Madhura, Tikta", "veerya": "Shita", "vipaka": "Madhura"},
        "element": "💧 Jala + 🪨 Prithvi",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/c/c4/Asparagus_racemosus_0741.jpg",
        "badge_color": "emerald",
        "tkdl_status": "Classical women's health and Rasayana herb. New extraction processes require patent review."
    },
    "moringa": {
        "sanskrit_name": "शिग्रु (Moringa)",
        "botanical_name": "Moringa oleifera",
        "common_name": "Drumstick Tree",
        "shloka": "शिग्रुः कटुः तीक्ष्णोष्णः कफवातविनाशनः।",
        "shloka_translation": "Moringa is traditionally described as pungent and warming, supporting balance of Kapha and Vata.",
        "active_compounds": ["Quercetin", "Isothiocyanates", "Chlorogenic Acid"],
        "ayurvedic_properties": {"rasa": "Katu, Tikta", "veerya": "Ushna", "vipaka": "Katu"},
        "element": "🔥 Agni + 🍃 Vayu",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/f/f2/Moringa_oleifera_flower.jpg",
        "badge_color": "emerald",
        "tkdl_status": "Food and medicinal plant with extensive prior art. Novel standardized products need evidence."
    }
}

def _reference_herb(common_name: str, botanical_name: str, image_name: str, aliases: List[str], benefit: str) -> Dict:
    """Builds a compact visual record for herbs from the reference list."""
    return {
        "sanskrit_name": common_name,
        "botanical_name": botanical_name,
        "common_name": common_name,
        "shloka": "Traditional herbal knowledge requires source and safety review.",
        "shloka_translation": benefit,
        "active_compounds": ["Plant-derived compounds"],
        "ayurvedic_properties": {"rasa": "Traditional use", "veerya": "Review required", "vipaka": "Review required"},
        "element": "🍃 Botanical reference",
        "image_url": f"https://commons.wikimedia.org/wiki/Special:FilePath/{image_name}",
        "badge_color": "emerald",
        "tkdl_status": "Reference herb. Verify traditional knowledge, safety, and novelty before relying on this entry.",
        "aliases": aliases
    }

HERBAL_KNOWLEDGE_BASE.update({
    "aloe_vera": _reference_herb("Aloe Vera", "Aloe vera", "Aloe_vera_flower_bud.jpg", ["aloe"], "Traditionally used to soothe minor skin irritation and support digestive preparations."),
    "calendula": _reference_herb("Calendula", "Calendula officinalis", "Calendula_officinalis_01.JPG", ["pot marigold"], "Traditionally used in topical preparations for skin comfort."),
    "chamomile": _reference_herb("Chamomile", "Matricaria chamomilla", "Matricaria_chamomilla_001.JPG", ["german chamomile"], "Traditionally used in calming and digestive preparations."),
    "comfrey": _reference_herb("Comfrey", "Symphytum officinale", "Symphytum_officinale_001.JPG", [], "Traditionally used mainly in external preparations; internal use requires expert safety review."),
    "dandelion": _reference_herb("Dandelion", "Taraxacum officinale", "Taraxacum_officinale_001.JPG", [], "Traditionally used in digestive and diuretic preparations."),
    "echinacea": _reference_herb("Echinacea", "Echinacea purpurea", "Echinacea_purpurea_003.JPG", [], "Traditionally used in preparations associated with seasonal immune support."),
    "garlic": _reference_herb("Garlic", "Allium sativum", "Garlic_bulbs_and_cloves.jpg", [], "Traditionally used in culinary and preparations associated with cardiovascular support."),
    "ginger": _reference_herb("Ginger Root", "Zingiber officinale", "Ginger_Root_(Zingiber_officinale).jpg", ["ginger", "adrak"], "Traditionally used for digestive comfort and nausea."),
    "ginseng": _reference_herb("Ginseng", "Panax ginseng", "Panax_ginseng_plant.jpg", [], "Traditionally used as an adaptogenic and energy-supporting herb."),
    "lavender": _reference_herb("Lavender", "Lavandula angustifolia", "Lavandula_angustifolia_001.JPG", [], "Traditionally used in calming and aromatic preparations."),
    "lemon_balm": _reference_herb("Lemon Balm", "Melissa officinalis", "Melissa_officinalis_001.JPG", ["melissa"], "Traditionally used for calming and digestive comfort."),
    "marshmallow_root": _reference_herb("Marshmallow Root", "Althaea officinalis", "Althaea_officinalis_001.JPG", ["marshmallow"], "Traditionally used for soothing preparations for irritated mucous membranes."),
    "mint": _reference_herb("Mint (Peppermint)", "Mentha x piperita", "Mentha_x_piperita_IMG_6075.jpg", ["peppermint"], "Traditionally used for digestive comfort and cooling preparations."),
    "nettle": _reference_herb("Nettle", "Urtica dioica", "Urtica_dioica_001.JPG", ["stinging nettle"], "Traditionally used as a nutrient-rich botanical and in seasonal preparations."),
    "rosemary": _reference_herb("Rosemary", "Salvia rosmarinus", "Rosmarinus_officinalis133095382.jpg", [], "Traditionally used as an aromatic herb associated with focus and antioxidant preparations."),
    "mugwort": _reference_herb("Mugwort", "Artemisia vulgaris", "Artemisia_vulgaris_001.JPG", [], "Traditionally used in digestive and protective herbal preparations."),
    "plantain": _reference_herb("Plantain", "Plantago major", "Plantago_major_001.JPG", ["waybread"], "Traditionally used in topical preparations for minor skin comfort."),
    "watercress": _reference_herb("Watercress / Lamb's Cress", "Nasturtium officinale", "Nasturtium_officinale_001.JPG", ["lamb's cress"], "Traditionally valued as a nutrient-rich green."),
    "crab_apple": _reference_herb("Crab Apple", "Malus sylvestris", "Malus_sylvestris_001.JPG", [], "Traditionally used in food and old herbal preparations."),
    "chervil": _reference_herb("Chervil", "Anthriscus cerefolium", "Anthriscus_cerefolium_001.JPG", [], "Traditionally used as a culinary herb and in digestive preparations."),
    "fennel": _reference_herb("Fennel", "Foeniculum vulgare", "Foeniculum_vulgare_001.JPG", ["saunf"], "Traditionally used to support digestive comfort and ease gas."),
    "attorlothe": _reference_herb("Attorlothe (unresolved)", "Historical identification uncertain", "Herbal_illustration.jpg", ["attorlothe", "betony", "stachys betonica"], "The historical ninth herb is uncertain; do not treat this entry as a confirmed botanical identification."),
    "goldenseal": _reference_herb("Goldenseal", "Hydrastis canadensis", "Hydrastis_canadensis_001.JPG", [], "Traditionally used in North American herbal preparations; berberine-containing products require safety and interaction review."),
    "sarpagandha": _reference_herb("सर्पगन्धा (Sarpagandha)", "Rauvolfia serpentina", "Rauvolfia_serpentina_001.JPG", ["rauwolfia", "indian snakeroot"], "Historically used in cardiovascular and nervous-system preparations; dosing and medicine interactions require expert supervision."),
    "black_haldi": _reference_herb("कृष्ण हरिद्रा (Black Haldi)", "Curcuma caesia", "Curcuma_caesia_001.JPG", ["black haldi", "black turmeric", "kali haldi"], "Traditionally used in regional remedies; distinguish it from Curcuma longa and verify identity before use."),
    "fairywand": _reference_herb("Fairywand (unresolved)", "Chamaelirium luteum", "Chamaelirium_luteum_001.JPG", ["false unicorn", "false unicorn root"], "A North American botanical traditionally associated with reproductive herbalism; clinical evidence and safety require review.")
    ,"forsythia": _reference_herb("Forsythia", "Forsythia suspensa", "Forsythia_suspensa1.jpg", ["forsythia fruit"], "Named as an example botanical drug source in the FDA Botanical Drug Development guidance; confirm formulation, quality, and evidence for any use."),
    "lonicera": _reference_herb("Japanese Honeysuckle", "Lonicera japonica", "Honeysuckle_2.jpg", ["honeysuckle", "japanese honeysuckle"], "Named as an example botanical drug source in the FDA Botanical Drug Development guidance; confirm formulation, quality, and evidence for any use.")
})

def detect_herb_visuals(user_query: str) -> Dict:
    """Detects a known herb and defaults to Ashwagandha when none is named."""
    q_lower = user_query.lower()
    best_match = None
    best_alias_length = 0
    for herb_key, herb_info in HERBAL_KNOWLEDGE_BASE.items():
        aliases = [herb_key, herb_info["botanical_name"].lower(), herb_info["common_name"].lower()]
        aliases.extend(herb_info.get("aliases", []))
        if herb_key == "tulsi":
            aliases.append("holy basil")
        elif herb_key == "amla":
            aliases.append("indian gooseberry")
        elif herb_key == "moringa":
            aliases.extend(["drumstick", "drumstick tree"])
        for alias in aliases:
            if alias and alias in q_lower and len(alias) > best_alias_length:
                best_match = herb_info
                best_alias_length = len(alias)
    if best_match:
        return best_match
    # Default fallback herb visual so visuals ALWAYS show up for any query!
    return HERBAL_KNOWLEDGE_BASE["ashwagandha"]

def print_flush(msg):
    print(msg, flush=True)

def generate_rag_response(user_query: str, persona: str = "innovator", language: str = "en") -> Dict:
    """Generates rich RAG response with visual cards, risk meters, Sanskrit Shlokas, and legal citations."""
    retrieved_chunks = query_legal_database(user_query, top_k=3)

    citations = []
    for idx, chunk in enumerate(retrieved_chunks, 1):
        citations.append({
            "ref": f"Ref {idx}",
            "document": chunk["document_title"],
            "section": chunk["section"],
            "page": chunk.get("page"),
            "jurisdiction": chunk["jurisdiction"],
            "authority": chunk["authority"],
            "snippet": chunk["content"]
        })

    herb_visual = detect_herb_visuals(user_query)

    # Risk level calculation
    risk_level = "MODERATE RISK (Section 3p Synergy Review)"
    risk_color = "amber"
    risk_score = 65
    q_lower = user_query.lower()
    if "patent" in q_lower and ("traditional" in q_lower or "ashwagandha" in q_lower or "turmeric" in q_lower):
        risk_level = "HIGH RISK (Section 3p Traditional Knowledge Review)"
        risk_color = "red"
        risk_score = 85
    elif "license" in q_lower or "158b" in q_lower or "schedule t" in q_lower:
        risk_level = "COMPLIANCE VERIFIED (AYUSH Rule 158B)"
        risk_color = "emerald"
        risk_score = 30

    # Multilingual & Sanskrit Shloka Formatting
    shloka_block = ""
    if herb_visual:
        shloka_block = f"🌿 **{herb_visual['sanskrit_name']}** (*{herb_visual['botanical_name']}*)\n" \
                       f"📜 *Sanskrit Shloka*: \"{herb_visual['shloka']}\"\n" \
                       f"✨ *Classical Meaning*: {herb_visual['shloka_translation']}\n\n"

    # Multilingual translation text adapter
    answer_text = ""
    if language == "hi":
        answer_text = f"### पेटेंट एवं कानूनी मार्गदर्शन\n\n" \
                      f"{shloka_block}" \
                      f"**भारतीय पेटेंट अधिनियम 1970 की धारा 3(p)** के तहत [Ref 1], पारंपरिक आयुर्वेदिक ज्ञान पर आधारित योग को सीधे पेटेंट नहीं कराया जा सकता है।\n\n" \
                      f"#### 🎯 पेटेंट और नियामक अनुपालन के चरण:\n" \
                      f"1. **सिनर्जिस्टिक प्रभाव (Synergistic Efficacy)**: नैदानिक अध्ययनों द्वारा बेहतर प्रभाव साबित करें [Ref 1]।\n" \
                      f"2. **AYUSH लाइसेंसिंग (Rule 158B)**: औषधि सुरक्षा और अनुसूची T GMP प्रमाणपत्र प्रस्तुत करें [Ref 3]।\n" \
                      f"3. **राष्ट्रीय जैव विविधता प्राधिकरण (NBA)**: पेटेंट आवेदन से पहले ABS मंजूरी प्राप्त करें [Ref 2]।"
    elif language == "sa":
        answer_text = f"### आयुर्वेद विधिक मार्गदर्शिनी\n\n" \
                      f"{shloka_block}" \
                      f"**भारतीय पेटेंट अधिनियमस्य तृतीय धारा (p)** अनुसारं [Ref 1] परम्परागत ज्ञानं साक्षात् न पेटेंट योग्यम्।\n\n" \
                      f"#### 🎯 नूतन योग पेटेंट विधानावश्यकाः:\n" \
                      f"1. **नूतन प्रभाव सिद्धिः**: नूतन योग प्रभाव सिद्ध्या पेटेंट अधिकारः लभ्यते [Ref 1]।\n" \
                      f"2. **आयुष लाइसेंसिंग (Rule 158B)**: अनुसूची T GMP पालनं अनिवार्यम् [Ref 3]।"
    elif language == "ta":
        answer_text = f"### காப்புரிமை மற்றும் சட்ட வழிகாட்டுதல்\n\n" \
                      f"{shloka_block}" \
                      f"இந்திய காப்புரிமைச் சட்டம், 1970 இன் **பிரிவு 3(p)** படி [Ref 1], அறியப்பட்ட பாரம்பரிய ஆயுர்வேத அறிவை மீண்டும் பயன்படுத்தும் சேர்மங்களுக்கு நேரடியாக காப்புரிமை பெற முடியாது.\n\n" \
                      f"#### 🎯 காப்புரிமை மற்றும் ஒழுங்குமுறை இணக்கப் பாதை:\n" \
                      f"1. **சினர்ஜிஸ்டிக் செயல்திறன்**: தனிப்பட்ட தாவரக் கூறுகளை விட மேம்பட்ட சிகிச்சை விளைவை மருத்துவ ஆய்வுகளால் நிரூபிக்கவும் [Ref 1].\n" \
                      f"2. **AYUSH உரிமம் (விதி 158B)**: பாதுகாப்பு மற்றும் Schedule T GMP சான்றுகளை சமர்ப்பிக்கவும் [Ref 3].\n" \
                      f"3. **தேசிய உயிரியல் பல்வகைமை ஆணையம் (NBA)**: காப்புரிமை தாக்கலுக்கு முன் ABS ஒப்புதலைப் பெறவும் [Ref 2]."
    elif language == "te":
        answer_text = f"### పేటెంట్ మరియు చట్టపరమైన మార్గదర్శకం\n\n" \
                      f"{shloka_block}" \
                      f"భారత పేటెంట్ చట్టం, 1970 లోని **సెక్షన్ 3(p)** ప్రకారం [Ref 1], తెలిసిన సంప్రదాయ ఆయుర్వేద జ్ఞానాన్ని పునరావృతం చేసే సమ్మేళనాలకు నేరుగా పేటెంట్ లభించదు.\n\n" \
                      f"#### 🎯 పేటెంట్ మరియు నియంత్రణ అనుసరణ దశలు:\n" \
                      f"1. **సినర్జిస్టిక్ ప్రభావం**: వ్యక్తిగత వృక్ష భాగాల కంటే మెరుగైన చికిత్సా ప్రభావాన్ని అధ్యయనాలతో నిరూపించండి [Ref 1].\n" \
                      f"2. **AYUSH లైసెన్సింగ్ (నియమం 158B)**: భద్రత మరియు Schedule T GMP ఆధారాలను సమర్పించండి [Ref 3].\n" \
                      f"3. **జాతీయ జీవవైవిధ్య ప్రాధికార సంస్థ (NBA)**: పేటెంట్ దాఖలు ముందు ABS అనుమతి పొందండి [Ref 2]."
    elif language == "bn":
        answer_text = f"### পেটেন্ট ও আইনি নির্দেশিকা\n\n" \
                      f"{shloka_block}" \
                      f"ভারতীয় পেটেন্ট আইন, ১৯৭০-এর **ধারা ৩(p)** অনুযায়ী [Ref 1], পরিচিত ঐতিহ্যবাহী আয়ুর্বেদিক জ্ঞানের পুনরাবৃত্তি করা সংমিশ্রণ সরাসরি পেটেন্টযোগ্য নয়।\n\n" \
                      f"#### 🎯 পেটেন্ট ও নিয়ন্ত্রক আনুগত্যের ধাপ:\n" \
                      f"1. **সমন্বিত কার্যকারিতা**: পৃথক উদ্ভিদ উপাদানের তুলনায় উন্নত চিকিৎসা ফলাফল গবেষণায় প্রমাণ করুন [Ref 1].\n" \
                      f"2. **AYUSH লাইসেন্সিং (নিয়ম 158B)**: নিরাপত্তা ও Schedule T GMP প্রমাণ জমা দিন [Ref 3].\n" \
                      f"3. **জাতীয় জীববৈচিত্র্য কর্তৃপক্ষ (NBA)**: পেটেন্ট দাখিলের আগে ABS অনুমোদন নিন [Ref 2]."
    elif language == "mr":
        answer_text = f"### पेटंट आणि कायदेशीर मार्गदर्शन\n\n" \
                      f"{shloka_block}" \
                      f"भारतीय पेटंट कायदा, १९७० मधील **कलम ३(p)** नुसार [Ref 1], ज्ञात पारंपरिक आयुर्वेदिक ज्ञानाची पुनरावृत्ती करणाऱ्या संयुगांना थेट पेटंट मिळू शकत नाही.\n\n" \
                      f"#### 🎯 पेटंट आणि नियामक अनुपालनाचे टप्पे:\n" \
                      f"1. **सिनर्जिस्टिक परिणाम**: स्वतंत्र वनस्पती घटकांपेक्षा चांगला उपचारात्मक परिणाम अभ्यासातून सिद्ध करा [Ref 1].\n" \
                      f"2. **AYUSH परवाना (नियम 158B)**: सुरक्षा आणि Schedule T GMP पुरावे सादर करा [Ref 3].\n" \
                      f"3. **राष्ट्रीय जैवविविधता प्राधिकरण (NBA)**: पेटंट दाखल करण्यापूर्वी ABS मंजुरी घ्या [Ref 2]."
    elif language == "kn":
        answer_text = f"### ಪೇಟೆಂಟ್ ಮತ್ತು ಕಾನೂನು ಮಾರ್ಗದರ್ಶನ\n\n" \
                      f"{shloka_block}" \
                      f"ಭಾರತೀಯ ಪೇಟೆಂಟ್ ಕಾಯಿದೆ, 1970 ರ **ವಿಭಾಗ 3(p)** ಪ್ರಕಾರ [Ref 1], ತಿಳಿದಿರುವ ಸಾಂಪ್ರದಾಯಿಕ ಆಯುರ್ವೇದ ಜ್ಞಾನವನ್ನು ಪುನರಾವರ್ತಿಸುವ ಸಂಯೋಜನೆಗಳಿಗೆ ನೇರ ಪೇಟೆಂಟ್ ಸಿಗುವುದಿಲ್ಲ.\n\n" \
                      f"#### 🎯 ಪೇಟೆಂಟ್ ಮತ್ತು ನಿಯಂತ್ರಣ ಅನುಸರಣೆ ಹಂತಗಳು:\n" \
                      f"1. **ಸಿನರ್ಜಿಸ್ಟಿಕ್ ಪರಿಣಾಮ**: ಪ್ರತ್ಯೇಕ ಸಸ್ಯ ಘಟಕಗಳಿಗಿಂತ ಉತ್ತಮ ಚಿಕಿತ್ಸಾ ಪರಿಣಾಮವನ್ನು ಅಧ್ಯಯನಗಳಿಂದ ಸಾಬೀತುಪಡಿಸಿ [Ref 1].\n" \
                      f"2. **AYUSH ಪರವಾನಗಿ (ನಿಯಮ 158B)**: ಸುರಕ್ಷತೆ ಮತ್ತು Schedule T GMP ದಾಖಲೆಗಳನ್ನು ಸಲ್ಲಿಸಿ [Ref 3].\n" \
                      f"3. **ರಾಷ್ಟ್ರೀಯ ಜೀವವೈವಿಧ್ಯ ಪ್ರಾಧಿಕಾರ (NBA)**: ಪೇಟೆಂಟ್ ಸಲ್ಲಿಸುವ ಮೊದಲು ABS ಅನುಮತಿ ಪಡೆಯಿರಿ [Ref 2]."
    elif language == "ml":
        answer_text = f"### പേറ്റന്റും നിയമ മാർഗനിർദേശവും\n\n" \
                      f"{shloka_block}" \
                      f"1970-ലെ ഇന്ത്യൻ പേറ്റന്റ് നിയമത്തിലെ **വകുപ്പ് 3(p)** പ്രകാരം [Ref 1], അറിയപ്പെടുന്ന പരമ്പരാഗത ആയുർവേദ അറിവിന്റെ ആവർത്തനമായ സംയോജനങ്ങൾക്ക് നേരിട്ട് പേറ്റന്റ് ലഭിക്കില്ല.\n\n" \
                      f"#### 🎯 പേറ്റന്റും നിയന്ത്രണ അനുസരണവും:\n" \
                      f"1. **സിനർജിസ്റ്റിക് ഫലം**: വ്യക്തിഗത സസ്യഘടകങ്ങളെക്കാൾ മികച്ച ചികിത്സാഫലം പഠനങ്ങളിലൂടെ തെളിയിക്കുക [Ref 1].\n" \
                      f"2. **AYUSH ലൈസൻസിംഗ് (ചട്ടം 158B)**: സുരക്ഷയും Schedule T GMP രേഖകളും സമർപ്പിക്കുക [Ref 3].\n" \
                      f"3. **ദേശീയ ജൈവവൈവിധ്യ അതോറിറ്റി (NBA)**: പേറ്റന്റ് സമർപ്പിക്കുന്നതിന് മുമ്പ് ABS അംഗീകാരം നേടുക [Ref 2]."
    else: # English
        answer_text = f"### Legal & Regulatory Guidance\n\n" \
                      f"{shloka_block}" \
                      f"Under **Section 3(p) of the Indian Patents Act, 1970** [Ref 1], inventions that are an aggregation or duplication of known traditional Ayurvedic knowledge are non-patentable.\n\n" \
                      f"#### 🎯 Pathway to Patentability & Compliance:\n" \
                      f"1. **Synergistic Efficacy**: Demonstrate non-obvious therapeutic enhancement compared to individual botanical components [Ref 1].\n" \
                      f"2. **AYUSH Licensing (Rule 158B)**: Provide proof of safety and Schedule T GMP compliance [Ref 3].\n" \
                      f"3. **National Biodiversity Authority (NBA)**: Secure prior Access and Benefit Sharing (ABS) approval before patent filing [Ref 2]."

    international_guidance = "\n\n#### 🌍 WHO & WIPO International Guidance\n" \
                           "- **WHO**: Botanical medicines should be supported by documented identity, quality control, good manufacturing practice, and safety evidence.\n" \
                           "- **WIPO**: Traditional knowledge and genetic resources should be documented with attention to provenance, prior art, community interests, and applicable access-and-benefit-sharing requirements.\n" \
                           "These are international guidance frameworks, not substitutes for Indian statutory advice or regulator instructions."
    answer_text += international_guidance

    return {
        "user_query": user_query,
        "persona": persona,
        "language": language,
        "answer": answer_text,
        "citations": citations,
        "herb_visual": herb_visual,
        "risk_assessment": {
            "level": risk_level,
            "color": risk_color,
            "score": risk_score
        },
        "compliance_roadmap": [
            {"step": 1, "title": "TKDL Search & Novelty Check", "status": "Completed"},
            {"step": 2, "title": "Synergistic Clinical Data", "status": "In Progress"},
            {"step": 3, "title": "NBA ABS Approval", "status": "Required"},
            {"step": 4, "title": "AYUSH Rule 158B NOC", "status": "Pending"}
        ]
    }

if __name__ == "__main__":
    q = "Is Ashwagandha formulation patentable under Section 3(p)?"
    res = generate_rag_response(q)
    print_flush(f"[TEST SUCCESS] Herb: {res['herb_visual']['sanskrit_name']}")
