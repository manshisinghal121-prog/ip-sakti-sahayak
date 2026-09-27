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
    "lonicera": _reference_herb("Japanese Honeysuckle", "Lonicera japonica", "Honeysuckle_2.jpg", ["honeysuckle", "japanese honeysuckle"], "Named as an example botanical drug source in the FDA Botanical Drug Development guidance; confirm formulation, quality, and evidence for any use."),
    "arjuna": _reference_herb("अर्जुन (Arjuna)", "Terminalia arjuna", "Terminalia_arjuna_tree.jpg", [], "Classical Ayurvedic heart-support herb; identity, dose, interactions, and evidence require professional review."),
    "ashoka": _reference_herb("अशोक (Ashoka)", "Saraca asoca", "Saraca_asoca_flowers.jpg", [], "Classical Ayurvedic botanical used in women's health preparations; verify formulation and safety evidence."),
    "haritaki": _reference_herb("हरीतकी (Haritaki)", "Terminalia chebula", "Terminalia_chebula_fruit.jpg", ["harad"], "Classical digestive and Rasayana botanical, commonly used in Triphala preparations."),
    "bibhitaki": _reference_herb("विभीतकी (Bibhitaki)", "Terminalia bellirica", "Terminalia_bellirica_fruit.jpg", ["baheda"], "Classical Ayurvedic fruit used in Triphala and traditional respiratory preparations."),
    "pippali": _reference_herb("पिप्पली (Pippali)", "Piper longum", "Piper_longum_fruit.jpg", ["long pepper"], "Traditional warming spice and Ayurvedic botanical; assess interactions and dose."),
    "shankhpushpi": _reference_herb("शंखपुष्पी (Shankhpushpi)", "Convolvulus pluricaulis", "Convolvulus_pluricaulis.jpg", ["shankhapushpi"], "Classical Medhya Rasayana botanical associated with memory and cognition traditions."),
    "yashtimadhu": _reference_herb("यष्टिमधु (Yashtimadhu)", "Glycyrrhiza glabra", "Glycyrrhiza_glabra_plant.jpg", ["licorice", "liquorice", "mulethi"], "Traditional soothing botanical; prolonged or high-dose use may have important interactions."),
    "manjistha": _reference_herb("मञ्जिष्ठा (Manjistha)", "Rubia cordifolia", "Rubia_cordifolia.jpg", ["manjishta"], "Classical Ayurvedic botanical used in traditional skin and blood-purification preparations."),
    "bhringraj": _reference_herb("भृंगराज (Bhringraj)", "Eclipta prostrata", "Eclipta_prostrata.jpg", ["bhringaraj", "false daisy"], "Traditional botanical used in hair and Rasayana preparations; verify topical or internal use."),
    "punarnava": _reference_herb("पुनर्नवा (Punarnava)", "Boerhavia diffusa", "Boerhavia_diffusa.jpg", [], "Classical Ayurvedic botanical used in traditional urinary and rejuvenative preparations."),
    "kalmegh": _reference_herb("कालमेघ (Kalmegh)", "Andrographis paniculata", "Andrographis_paniculata.jpg", ["andrographis", "king of bitters"], "Bitter botanical used in traditional digestive and seasonal wellness preparations."),
    "kutki": _reference_herb("कुटकी (Kutki)", "Picrorhiza kurroa", "Picrorhiza_kurroa.jpg", ["katuki"], "High-altitude Ayurvedic botanical with conservation considerations; verify identity and sourcing."),
    "sariva": _reference_herb("सारिवा (Sariva)", "Hemidesmus indicus", "Hemidesmus_indicus.jpg", ["anantamul", "indian sarsaparilla"], "Traditional cooling and digestive botanical; check source authentication."),
    "gokshura": _reference_herb("गोक्षुर (Gokshura)", "Tribulus terrestris", "Tribulus_terrestris.jpg", ["gokhru", "puncture vine"], "Traditional urinary and vitality botanical; product claims require evidence review."),
    "vidanga": _reference_herb("विडंग (Vidanga)", "Embelia ribes", "Embelia_ribes.jpg", ["vaividang"], "Classical Ayurvedic botanical traditionally used in digestive preparations."),
    "vacha": _reference_herb("वचा (Vacha)", "Acorus calamus", "Acorus_calamus.jpg", ["sweet flag"], "Traditional botanical requiring careful identity, regulatory, and safety review."),
    "jatamansi": _reference_herb("जटामांसी (Jatamansi)", "Nardostachys jatamansi", "Nardostachys_jatamansi.jpg", ["spikenard"], "Protected Himalayan botanical used in traditional calming preparations; verify conservation-compliant sourcing."),
    "musta": _reference_herb("मुस्ता (Musta)", "Cyperus rotundus", "Cyperus_rotundus.jpg", ["nagarmotha", "nutgrass"], "Classical digestive and aromatic Ayurvedic botanical."),
    "tagara": _reference_herb("तगर (Tagara)", "Valeriana wallichii", "Valeriana_wallichii.jpg", ["indian valerian"], "Traditional calming botanical; assess sedative interactions with a clinician."),
    "bael": _reference_herb("बिल्व (Bael)", "Aegle marmelos", "Aegle_marmelos_fruit.jpg", ["bilva", "bel fruit", "wood apple"], "Classical digestive fruit and Ayurvedic botanical."),
    "isabgol": _reference_herb("इसबगोल (Isabgol)", "Plantago ovata", "Plantago_ovata.jpg", ["psyllium", "ispaghula"], "Fiber-rich botanical used for digestive support; take with adequate water and review medicines."),
    "senna": _reference_herb("Senna", "Senna alexandrina", "Senna_alexandrina.jpg", ["senna leaf"], "Traditional laxative botanical; prolonged use and interactions require professional guidance."),
    "cinnamon": _reference_herb("दालचीनी (Cinnamon)", "Cinnamomum verum", "Cinnamomum_verum_bark.jpg", ["dalchini", "true cinnamon"], "Aromatic culinary and traditional botanical; distinguish cinnamon species and preparations."),
    "clove": _reference_herb("लवंग (Clove)", "Syzygium aromaticum", "Syzygium_aromaticum_cloves.jpg", ["laung"], "Aromatic botanical used traditionally in oral and digestive preparations."),
    "cardamom": _reference_herb("एला (Cardamom)", "Elettaria cardamomum", "Elettaria_cardamomum.jpg", ["elaichi", "green cardamom"], "Aromatic culinary and traditional digestive botanical."),
    "black_pepper": _reference_herb("मरिच (Black Pepper)", "Piper nigrum", "Piper_nigrum_fruit.jpg", ["black pepper", "kali mirch", "maricha"], "Traditional warming spice; piperine may affect medicine absorption and interactions.")
})

for herb_key, herb_info in HERBAL_KNOWLEDGE_BASE.items():
    local_name = re.sub(r"[^a-z0-9]+", "-", herb_key.lower()).strip("-")
    herb_info["local_image_url"] = f"/assets/herbs/{local_name}.jpg"

def detect_herb_visuals(user_query: str) -> Dict:
    """Detect a known herb without inventing one when none is named."""
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
    # IMPORTANT: do not invent a herb when the user did not name one.
    return None

def print_flush(msg):
    print(msg, flush=True)

def detect_question_focus(user_query: str) -> Optional[str]:
    """Maps common user questions to a focused guidance topic."""
    query = user_query.lower().strip()
    focus_terms = {
        "patentability": ["patent", "patentable", "novelty", "prior art", "section 3", "tkdl"],
        "ayush licensing": ["ayush", "license", "licence", "158b", "schedule t", "gmp"],
        "safety and use": ["safe", "safety", "side effect", "interaction", "dosage", "contraindication", "pregnan"],
        "biodiversity and abs": ["biodiversity", "nba", "benefit sharing", "abs", "genetic resource", "biological diversity"],
        "who and wipo guidance": ["who", "wipo", "world health", "traditional knowledge guideline"],
        "herb identity and traditional use": ["what is", "benefit", "uses", "used for", "botanical name", "scientific name"]
    }
    for focus, terms in focus_terms.items():
        if any(term in query for term in terms):
            return focus
    return None


def focused_guidance(focus: Optional[str], herb_visual: Optional[Dict]) -> str:
    """Short context used internally; the user-facing answer is synthesized below."""
    if not focus:
        return ""
    return ""


def _question_intent(query: str) -> str:
    """Detect the user's action/question type so answers are phrased naturally."""
    q = query.lower().strip()
    if re.search(r"\b(can i|can we|is .* patentable|eligible|allowed)\b", q):
        return "eligibility"
    if re.search(r"\b(what is|what are|meaning of|define|explain)\b", q):
        return "explain"
    if re.search(r"\b(how do i|how can i|how to|steps|process|procedure)\b", q):
        return "howto"
    if re.search(r"\b(which|what .* license|what .* documents|what .* requirements)\b", q):
        return "requirements"
    if re.search(r"\b(why|reason|difference)\b", q):
        return "why"
    return "general"


def _clean_sentence(text: str) -> str:
    """Make retrieved text readable without changing its substance."""
    text = re.sub(r"\s+", " ", str(text)).strip()
    text = re.sub(r"^[-*•]\s*", "", text)
    return text


def _source_sentences(chunks: List[Dict], query: str, limit: int = 4) -> List[str]:
    """Select the most query-relevant source sentences for evidence-grounded synthesis."""
    q_tokens = {
        t for t in re.findall(r"[a-zA-Z0-9]{3,}", query.lower())
        if t not in {
            "what", "when", "where", "which", "this", "that", "with", "from", "about",
            "have", "does", "do", "can", "could", "would", "should", "please", "tell",
            "give", "under", "into", "your", "they", "their", "there", "some"
        }
    }
    candidates = []
    for chunk in chunks:
        raw = _clean_sentence(chunk.get("content", ""))
        for sentence in re.split(r"(?<=[.!?])\s+", raw):
            s = _clean_sentence(sentence)
            if len(s) < 35:
                continue
            tokens = set(re.findall(r"[a-zA-Z0-9]{3,}", s.lower()))
            overlap = len(tokens & q_tokens)
            # Prefer legally meaningful short passages and avoid huge source dumps.
            score = overlap * 3
            if any(k in s.lower() for k in ["section", "rule", "schedule", "patent", "prior art", "benefit sharing", "safety", "gmp", "ayush"]):
                score += 2
            if len(s) > 420:
                score -= 1
            candidates.append((score, s))
    candidates.sort(key=lambda item: (-item[0], len(item[1])))
    selected = []
    seen = set()
    for _, sentence in candidates:
        key = sentence.lower()
        if key in seen:
            continue
        seen.add(key)
        selected.append(sentence)
        if len(selected) >= limit:
            break
    return selected


def _normalize_language(language: Optional[str]) -> str:
    """Normalize language values coming from the frontend/API."""
    value = str(language or "en").strip().lower()
    aliases = {
        "english": "en",
        "en-us": "en",
        "en-in": "en",
        "hindi": "hi",
        "hindi (हिंदी)": "hi",
        "हिंदी": "hi",
        "हिन्दी": "hi",
        "hi-in": "hi",
        "sanskrit": "sa",
        "संस्कृत": "sa",
    }
    return aliases.get(value, value)


def _hindi_herb_description(herb_visual: Dict) -> str:
    """Return a Hindi description for the main Ayurvedic herb records."""
    key = str(herb_visual.get("common_name", "")).strip().lower()
    botanical = str(herb_visual.get("botanical_name", "")).strip().lower()

    descriptions = {
        "indian ginseng": "अश्वगंधा को पारंपरिक आयुर्वेदिक ज्ञान में वात को संतुलित करने वाली, शारीरिक शक्ति बढ़ाने वाली और रसायन के रूप में वर्णित किया गया है। इसे उष्ण वीर्य वाला माना जाता है।",
        "turmeric": "हरिद्रा को पारंपरिक आयुर्वेदिक ज्ञान में कटु और तिक्त गुणों वाली तथा उष्ण वीर्य वाली माना गया है। इसे त्वचा और घाव से जुड़ी पारंपरिक तैयारियों में भी वर्णित किया जाता है।",
        "amrita / heart-leaved moonseed": "गुडूची को पारंपरिक आयुर्वेदिक ज्ञान में तिक्त, रसायन और पाचन को सहारा देने वाली वनस्पति के रूप में वर्णित किया गया है।",
        "holy basil": "तुलसी को पारंपरिक रूप से सुगंधित और उष्ण वनस्पति माना जाता है तथा इसे श्वसन और शुद्धिकरण से जुड़ी पारंपरिक तैयारियों में उपयोग किया जाता है।",
        "neem": "नीम को पारंपरिक रूप से शीतल, हल्का और तिक्त माना जाता है। इसे त्वचा और अन्य पारंपरिक तैयारियों में उपयोग किया जाता है।",
        "brahmi": "ब्राह्मी को पारंपरिक आयुर्वेदिक ज्ञान में स्मृति, मेधा, रसायन और जीवन शक्ति से जोड़ा जाता है।",
        "indian gooseberry": "आमलकी को पारंपरिक रूप से रसायन फल माना जाता है और इसे पोषण तथा जीवन शक्ति से जोड़ा जाता है।",
        "wild asparagus": "शतावरी को पारंपरिक रूप से पोषक, बलवर्धक और रसायन वनस्पति के रूप में वर्णित किया जाता है।",
        "drumstick tree": "मोरिंगा को पारंपरिक रूप से कटु और उष्ण माना जाता है तथा इसे कफ और वात संतुलन से जोड़ा जाता है।",
    }

    if key in descriptions:
        return descriptions[key]

    # A small fallback for the extended reference herb list.
    if "aloe" in key or "aloe" in botanical:
        return "एलोवेरा का उपयोग पारंपरिक रूप से त्वचा को आराम देने वाली और कुछ पाचन संबंधी तैयारियों में किया जाता है।"
    if "ginger" in key or "zingiber" in botanical:
        return "अदरक का उपयोग पारंपरिक रूप से पाचन संबंधी आराम और मतली से जुड़ी तैयारियों में किया जाता है।"
    if "ginseng" in key or "panax" in botanical:
        return "जिनसेंग का उपयोग पारंपरिक रूप से ऊर्जा और सामान्य स्वास्थ्य से जुड़ी तैयारियों में किया जाता है।"

    original = str(herb_visual.get("shloka_translation", "")).strip()
    if original:
        return (
            "इस वनस्पति के बारे में उपलब्ध रिकॉर्ड में पारंपरिक उपयोग का विवरण दिया गया है। "
            "विस्तृत उपयोग के लिए संबंधित मूल स्रोत और सुरक्षा जानकारी की जाँच करना आवश्यक है।"
        )
    return "इस वनस्पति के पारंपरिक उपयोग का रिकॉर्ड उपलब्ध है, लेकिन वर्तमान जानकारी में पर्याप्त विवरण नहीं है।"


def synthesize_natural_answer(
    user_query: str,
    category: Optional[str],
    focus: Optional[str],
    herb_visual: Optional[Dict],
    relevant_chunks: List[Dict],
    language: str = "en",
    persona: str = "innovator",
) -> str:
    """Create a direct conversational answer in the language selected by the user."""
    language = _normalize_language(language)
    intent = _question_intent(user_query)
    category = category or "General"
    subject = None

    if herb_visual:
        subject = f"{herb_visual['common_name']} ({herb_visual['botanical_name']})"

    # ---------------------------------------------------------
    # HINDI ANSWER
    # ---------------------------------------------------------
    if language == "hi":
        # Herb questions should be answered from the herb record first.
        if herb_visual and focus == "herb identity and traditional use":
            description = _hindi_herb_description(herb_visual)
            return (
                f"**{subject}** के बारे में आपके प्रश्न का उत्तर उपलब्ध हर्ब रिकॉर्ड के आधार पर है।\n\n"
                f"{description}\n\n"
                "यह पारंपरिक उपयोग की जानकारी है। इसे हर व्यक्ति के लिए प्रभावशीलता या सुरक्षा का प्रमाण नहीं माना जाना चाहिए। "
                "किसी उत्पाद या चिकित्सीय उपयोग के लिए तैयारी, मात्रा, संभावित दवा-परस्पर क्रिया और उपलब्ध वैज्ञानिक प्रमाण की अलग से जाँच करनी चाहिए।"
            )

        source_points = _source_sentences(relevant_chunks, user_query, limit=4)
        evidence = " ".join(source_points[:3])

        if category == "Patentability" or focus == "patentability":
            if intent == "eligibility":
                opening = "संभव है, लेकिन केवल किसी जड़ी-बूटी या उसके पारंपरिक उपयोग के आधार पर पेटेंटेबिलिटी तय नहीं होती।"
            else:
                opening = "पेटेंटेबिलिटी के प्रश्न में मुख्य बात यह देखना है कि आपके दावे में वास्तव में नया क्या है। केवल यह तथ्य कि कोई सामग्री पहले से ज्ञात है या नहीं है, पर्याप्त नहीं है।"
            middle = (
                "व्यावहारिक समीक्षा में नवीनता और prior art को देखना चाहिए। इसमें दस्तावेजीकृत पारंपरिक ज्ञान भी शामिल हो सकता है। "
                "इसके बाद लागू पेटेंट आवश्यकताओं और exclusions की जाँच करनी चाहिए।"
            )
            if source_points:
                middle += " उपलब्ध स्रोत सामग्री में भी इसी प्रकार के बिंदु मिलते हैं: " + evidence
            return (
                opening + " " + middle +
                " यदि आप अपनी exact formulation, process या claimed use बताएं तो मैं उसी के अनुसार विश्लेषण को अधिक specific कर सकता हूँ।"
            )

        if category in {"AYUSH_Licensing", "Regulatory_Compliance"} or focus == "ayush licensing":
            if intent == "requirements":
                opening = "सटीक आवश्यकताएँ इस बात पर निर्भर करती हैं कि आपका उत्पाद क्या है और वह classical formulation है या modified/new formulation।"
            elif intent == "howto":
                opening = "पहले उत्पाद की सही regulatory category तय करें। इसके बाद उसी category के अनुसार licensing और manufacturing requirements को map करें।"
            else:
                opening = "AYUSH compliance के प्रश्न में सबसे पहले product category तय करना जरूरी है क्योंकि licensing pathway उसी पर निर्भर करता है।"
            middle = (
                "इसके बाद लागू licensing route, manufacturing controls, safety और evidence requirements, documentation तथा GMP provisions की जाँच करनी चाहिए।"
            )
            if source_points:
                middle += " उपलब्ध स्रोतों में विशेष रूप से ये बिंदु मिलते हैं: " + evidence
            return (
                opening + " " + middle +
                " यदि आप product type और manufacturing arrangement बताएं तो मैं checklist को अधिक specific कर सकता हूँ।"
            )

        if category == "Safety" or focus == "safety and use":
            opening = (
                f"**{subject}** की safety उसकी exact preparation, मात्रा, उपयोग के तरीके और उपयोग करने वाले व्यक्ति पर निर्भर करती है।"
                if subject else
                "Safety exact preparation, मात्रा, उपयोग के तरीके और उपयोग करने वाले व्यक्ति पर निर्भर करती है।"
            )
            middle = (
                "पारंपरिक उपयोग को safety या effectiveness का प्रमाण नहीं माना जाना चाहिए। "
                "Contraindications, दवाओं के साथ interactions, botanical identity और material quality पर विशेष ध्यान देना चाहिए।"
            )
            if source_points:
                middle += " उपलब्ध evidence भी इन पहलुओं पर ध्यान देने की आवश्यकता बताता है: " + evidence
            return middle + " " + "यदि आप preparation और intended use बताएं तो मैं उत्तर को अधिक specific कर सकता हूँ।"

        if category == "Biodiversity_ABS" or focus == "biodiversity and abs":
            opening = (
                "यदि आपका काम किसी Indian biological resource या उससे जुड़े traditional knowledge का उपयोग करता है तो biodiversity और access-and-benefit-sharing requirements लागू हो सकती हैं।"
            )
            middle = (
                "अगला कदम resource की पहचान करना, यह देखना है कि वह कहाँ से और कैसे प्राप्त हुआ, उसका उपयोग क्या है और क्या आपकी activity applicable approval या benefit-sharing framework के अंतर्गत आती है।"
            )
            if source_points:
                middle += " उपलब्ध स्रोत सामग्री में ये संबंधित बिंदु मिलते हैं: " + evidence
            return opening + " " + middle + " Exact obligation आपके activity के facts पर निर्भर करेगी।"

        if category == "Traditional_Knowledge" or focus == "herb identity and traditional use":
            opening = (
                "मुख्य बात यह है कि संबंधित ज्ञान या उपयोग पहले से documented है या नहीं। "
                "यदि documented है तो वह prior art या traditional-knowledge evidence के रूप में relevant हो सकता है।"
            )
            if source_points:
                opening += " उपलब्ध स्रोत सामग्री में संबंधित बिंदु हैं: " + evidence
            return opening + " यदि आप herb, formulation या traditional use बताएं तो मैं उसी specific case से जोड़कर समझा सकता हूँ।"

        if category == "WIPO_Guidance":
            opening = "WIPO की सामग्री traditional knowledge, genetic resources और संबंधित IP rights के लिए एक international framework देती है।"
        elif category == "WHO_Guidance":
            opening = "WHO की सामग्री traditional medicine, botanical quality, safety और manufacturing से जुड़े evidence और guidance के लिए उपयोगी है।"
        else:
            opening = "आपके प्रश्न से सीधे संबंधित उपलब्ध जानकारी यह है:"

        if source_points:
            return opening + "\n\n" + evidence
        return opening + "\n\nवर्तमान knowledge base में इस प्रश्न का विश्वसनीय उत्तर देने के लिए पर्याप्त सीधे संबंधित evidence नहीं मिला।"

    # ---------------------------------------------------------
    # ENGLISH ANSWER
    # ---------------------------------------------------------
    # Keep the existing English behaviour unchanged.
    if herb_visual and focus == "herb identity and traditional use":
        description = str(herb_visual.get("shloka_translation", "")).strip()
        if description:
            return (
                f"You’re asking about **{subject}**. Traditionally, it is described in the knowledge base as {description.lower()} "
                f"This is traditional-use context, not proof that the herb is effective or safe for every person. "
                f"For a product or medical use, the preparation, dose, interactions, and supporting evidence still need to be checked."
            )
        return (
            f"You’re asking about **{subject}**. I found its botanical record, but the current knowledge base does not contain enough detail "
            f"to give a reliable use summary. I’d rather say that than invent a medical claim."
        )

    source_points = _source_sentences(relevant_chunks, user_query, limit=4)
    evidence = " ".join(source_points[:3])

    if category == "Patentability" or focus == "patentability":
        if intent == "eligibility":
            opening = "Possibly, but the herb or a traditional use by itself is not enough to establish patentability."
        else:
            opening = "For a patentability question, the important issue is what is actually new in your claim—not simply whether the ingredient is known."
        middle = (
            "The practical review should look at novelty and prior art, including documented traditional knowledge, then check the other applicable patent requirements and exclusions."
        )
        if source_points:
            middle += " The retrieved material is consistent with that approach and highlights " + evidence
        return opening + " " + middle + " If you share the exact formulation, process, or claimed use, I can narrow the analysis to that specific case."

    if category in {"AYUSH_Licensing", "Regulatory_Compliance"} or focus == "ayush licensing":
        if intent == "requirements":
            opening = "The exact requirements depend on what your product is and whether it follows a classical formulation or is a modified/new formulation."
        elif intent == "howto":
            opening = "A sensible way to approach this is to classify the product first, then map the licensing and manufacturing requirements to that category."
        else:
            opening = "For an AYUSH compliance question, the product category comes first because the licensing pathway depends on it."
        middle = "From there, review the applicable licensing route, manufacturing controls, safety/evidence requirements, documentation, and GMP provisions."
        if source_points:
            middle += " The retrieved sources specifically point to " + evidence
        return opening + " " + middle + " Tell me the product type and whether you manufacture it yourself, and I can make the checklist more specific."

    if category == "Safety" or focus == "safety and use":
        opening = f"For **{subject}**, safety depends on the exact preparation, amount, route of use, and the person using it." if subject else "Safety depends on the exact preparation, amount, route of use, and the person using it."
        middle = "Traditional use is useful context, but it should not be treated as proof of safety or effectiveness. Particular attention should be given to contraindications, medicine interactions, identity and quality of the material."
        if source_points:
            middle += " The retrieved evidence also emphasizes " + evidence
        return opening + " " + middle + " I can make this more specific if you tell me the preparation and intended use."

    if category == "Biodiversity_ABS" or focus == "biodiversity and abs":
        opening = "If your work uses an Indian biological resource or associated traditional knowledge, biodiversity and access-and-benefit-sharing requirements may become relevant."
        middle = "The next step is to identify the resource, how it was obtained, how it will be used, and whether your activity falls within the applicable approval or benefit-sharing framework."
        if source_points:
            middle += " The retrieved material points to " + evidence
        return opening + " " + middle + " The exact obligation depends on the facts of the activity, so those details matter."

    if category == "Traditional_Knowledge" or focus == "herb identity and traditional use":
        opening = "The key point is whether the knowledge or use is already documented and therefore relevant as prior art or as traditional-knowledge evidence."
        if source_points:
            opening += " In the retrieved material, the most relevant points are " + evidence
        return opening + " If you tell me the herb, formulation, or traditional use you are referring to, I can connect the answer to that specific case."

    if category == "WIPO_Guidance":
        opening = "WIPO material is most useful here as an IP framework for traditional knowledge, genetic-resource context and related rights."
    elif category == "WHO_Guidance":
        opening = "WHO material is most useful here for evidence and guidance around traditional medicine, botanical quality, safety and manufacturing."
    else:
        opening = "Here’s the part of the available evidence that directly relates to your question."

    if source_points:
        return opening + " " + evidence
    return opening + " I could not find enough directly relevant evidence in the current knowledge base to answer this confidently."


def generate_rag_response(
    user_query: str,
    persona: str = "innovator",
    language: str = "en",
    ml_category: Optional[str] = None
) -> Dict:
    """Generates a natural, query-focused RAG response with supporting citations."""
    routing_terms = {
        "Patentability": "patentability patent novelty prior art Section 3 traditional knowledge",
        "AYUSH_Licensing": "AYUSH licensing Rule 158B Schedule T GMP regulatory compliance",
        "Safety": "safety dosage contraindications side effects interactions quality",
        "Biodiversity_ABS": "biodiversity biological resources access benefit sharing NBA ABS",
        "Traditional_Knowledge": "traditional knowledge TKDL prior art Ayurveda",
        "Regulatory_Compliance": "regulatory compliance AYUSH licensing GMP requirements",
        "WIPO_Guidance": "WIPO intellectual property traditional knowledge genetic resources",
        "WHO_Guidance": "WHO traditional medicine botanical quality safety GMP guidance"
    }

    # Use the user's original wording first so exact legal references such as
    # Section 3(p) are preserved. Then use the ML-routed query as a second
    # retrieval pass for broader contextual evidence.
    rag_query = user_query + (" " + routing_terms[ml_category] if ml_category in routing_terms else "")

    primary_chunks = query_legal_database(user_query, top_k=5)
    routed_chunks = query_legal_database(rag_query, top_k=5) if rag_query != user_query else []

    # Merge by chunk_id while preserving the primary (exact-query) ranking first.
    # This prevents routing terms from pushing an exact legal provision out of
    # the evidence set.
    retrieved_chunks = []
    seen_chunk_ids = set()

    for chunk in primary_chunks + routed_chunks:
        chunk_id = chunk.get("chunk_id") or (
            chunk.get("document_title", ""),
            chunk.get("section", ""),
            chunk.get("page"),
            chunk.get("content", "")[:120],
        )
        if chunk_id in seen_chunk_ids:
            continue
        seen_chunk_ids.add(chunk_id)
        retrieved_chunks.append(chunk)

    # Keep the evidence set compact for answer synthesis/citations.
    retrieved_chunks = retrieved_chunks[:6]


    herb_visual = detect_herb_visuals(user_query)
    question_focus = detect_question_focus(user_query)

    # Do not allow a weak/incorrect ML label to dominate an obvious question focus.
    focus_to_category = {
        "patentability": "Patentability",
        "ayush licensing": "AYUSH_Licensing",
        "safety and use": "Safety",
        "biodiversity and abs": "Biodiversity_ABS",
        "who and wipo guidance": "WIPO_Guidance",
        "herb identity and traditional use": "Traditional_Knowledge",
    }
    category = ml_category if ml_category in routing_terms else focus_to_category.get(question_focus, ml_category)

    relevant_chunks = [
        chunk for chunk in retrieved_chunks
        if float(chunk.get("relevance_score", 0)) >= 0.12
    ]
    if not relevant_chunks and retrieved_chunks:
        relevant_chunks = [retrieved_chunks[0]]

    # Build clean citations from the evidence actually used for the answer.
    # Keep the strongest passage from each source document so repeated chunks
    # from the same document do not clutter the UI.
    citation_by_document = {}

    for chunk in relevant_chunks:
        document = str(chunk.get("document_title", "Source") or "Source").strip()
        document_key = document.lower()

        score = float(chunk.get("relevance_score", 0) or 0)
        exact_ref = float(chunk.get("exact_reference_score", 0) or 0)

        existing = citation_by_document.get(document_key)
        if existing is None:
            citation_by_document[document_key] = chunk
        else:
            existing_score = float(existing.get("relevance_score", 0) or 0)
            existing_exact = float(existing.get("exact_reference_score", 0) or 0)

            if (exact_ref, score) > (existing_exact, existing_score):
                citation_by_document[document_key] = chunk

    def _source_type(chunk: Dict) -> str:
        """Classify evidence without altering source metadata."""
        title = str(chunk.get("document_title", "")).lower()
        source = str(chunk.get("knowledge_source", "")).lower()

        if any(term in title for term in [
            "patent_act", "biodiversity_act", "drugs and cosmetics act",
            "rule 158b", "patents act"
        ]):
            return "Primary legal text"

        if "legal/regulatory" in source:
            return "Legal / regulatory source"

        if "wipo" in title or "who" in title:
            return "International guidance"

        if "tkdl" in title:
            return "Traditional-knowledge reference"

        return "Reference / guidance"

    # Put exact-reference matches first, then strongest relevance.
    citation_chunks = sorted(
        citation_by_document.values(),
        key=lambda chunk: (
            float(chunk.get("exact_reference_score", 0) or 0),
            float(chunk.get("relevance_score", 0) or 0),
        ),
        reverse=True,
    )[:6]

    citations = []
    for idx, chunk in enumerate(citation_chunks, 1):
        citations.append({
            "ref": f"Ref {idx}",
            "document": chunk.get("document_title", "Source"),
            "section": chunk.get("section", ""),
            "page": chunk.get("page"),
            "jurisdiction": chunk.get("jurisdiction", "India"),
            "authority": chunk.get("authority", ""),
            "source_type": _source_type(chunk),
            "relevance_score": round(
                float(chunk.get("relevance_score", 0) or 0), 4
            ),
            "snippet": chunk.get("content", "")
        })

    answer_text = synthesize_natural_answer(
        user_query=user_query,
        category=category,
        focus=question_focus,
        herb_visual=herb_visual,
        relevant_chunks=relevant_chunks,
        language=language,
        persona=persona,
    )

    # Keep the answer conversational; citations are already exposed separately in the UI.
    if language == "hi":
        if relevant_chunks:
            answer_text += f"\n\nमैंने इस उत्तर के लिए {len(citations)} संबंधित स्रोत passage की जाँच की है।"
        else:
            answer_text += "\n\nइस प्रश्न के लिए पर्याप्त रूप से संबंधित source passage नहीं मिला।"
    else:
        if relevant_chunks:
            answer_text += f"\n\nI checked {len(citations)} relevant source passage(s) for this response."
        else:
            answer_text += "\n\nI did not find a sufficiently relevant source passage for this question."

    q_lower = user_query.lower()
    risk_level = "MODERATE RISK"
    risk_color = "amber"
    risk_score = 50
    if category == "Patentability" and any(k in q_lower for k in ["traditional knowledge", "tkdl", "section 3(p)", "section 3p"]):
        risk_level = "REVIEW REQUIRED — Traditional Knowledge / Section 3(p)"
        risk_color = "red"
        risk_score = 80
    elif category in {"AYUSH_Licensing", "Regulatory_Compliance"}:
        risk_level = "COMPLIANCE REVIEW REQUIRED"
        risk_color = "amber"
        risk_score = 55

    roadmap = [
        {"step": 1, "title": "Define the exact question or product", "status": "Current"},
        {"step": 2, "title": "Review the relevant evidence and source", "status": "Current"},
        {"step": 3, "title": "Validate against the applicable authority", "status": "Recommended"},
    ]

    return {
        "user_query": user_query,
        "persona": persona,
        "language": _normalize_language(language),
        "question_focus": question_focus,
        "answer": answer_text,
        "citations": citations,
        "herb_visual": herb_visual,
        "risk_assessment": {
            "level": risk_level,
            "color": risk_color,
            "score": risk_score
        },
        "compliance_roadmap": roadmap
    }


if __name__ == "__main__":
    q = "What are the traditional uses of Ashwagandha?"
    res = generate_rag_response(q)
    print_flush(res["answer"])
