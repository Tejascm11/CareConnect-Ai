import os
import sqlite3
import tempfile
from datetime import datetime
import streamlit as st
from deep_translator import GoogleTranslator
translator = GoogleTranslator(source="auto", target="en")

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="AI Medical Chatbot", page_icon="🩺")

st.title("🩺 AI Medical Chatbot")
st.caption("Simple medical assistant")

# ---------------- MEDICAL DATABASE ----------------

medical_db = {
    "fever": (
        "General Illness",
        "Fever usually occurs due to viral or bacterial infections.\n"
        "It is the body's natural response to fight infection.",
        "Paracetamol helps reduce fever and body pain.\n"
        "Avoid antibiotics unless prescribed by a doctor.",
        "• Take complete rest\n• Drink warm fluids\n• Eat light food",
        "See doctor if fever lasts more than 2 days"
    ),
    "diabetes": (
    "Metabolic Disorder",
    "Diabetes occurs when blood sugar levels remain high because the body "
    "does not produce enough insulin or cannot use it properly.",
    "Blood sugar monitoring and doctor-advised medicines help manage diabetes.\n"
    "Avoid self-medication.",
    "• Avoid sugary foods and soft drinks\n"
    "• Eat vegetables and whole grains\n"
    "• Exercise regularly (walking, yoga)\n"
    "• Maintain healthy body weight\n"
    "• Drink sufficient water",
    "If sugar levels remain high or symptoms worsen, consult a doctor immediately"
    ),
    "cold": (
        "General Illness",
        "Common cold is caused by viral infection of the nose and throat.\n"
        "It spreads through air and close contact.",
        "Antihistamines reduce sneezing and runny nose.\n"
        "Paracetamol can be taken if fever is present.",
        "• Steam inhalation\n• Warm fluids\n• Proper rest",
        "If symptoms worsen or breathing difficulty occurs"
    ),

    "cough": (
        "Respiratory",
        "Cough occurs due to throat irritation, infection, or allergy.\n"
        "Smoking and pollution can worsen it.",
        "Cough syrups provide temporary relief.\n"
        "Persistent cough needs medical evaluation.",
        "• Drink warm water\n• Avoid smoking\n• Steam inhalation",
        "If cough lasts more than 7 days"
    ),

    "heart failure": (
        "Cardiac",
        "Heart failure occurs when the heart cannot pump blood effectively.\n"
        "It is often caused by long-term heart disease or high BP.",
        "Requires lifelong medical treatment under cardiologist supervision.\n"
        "Do not self-medicate.",
        "• Low-salt diet\n• Avoid heavy work\n• Take medicines regularly",
        "URGENT – Consult cardiologist"
    ),

    "heart attack": (
        "Cardiac",
        "Heart attack occurs due to blockage of blood supply to heart muscles.\n"
        "It is a life-threatening emergency.",
        "Immediate emergency treatment is required.\n"
        "Do not delay or self-treat.",
        "• Keep patient calm\n• Loosen tight clothing",
        "EMERGENCY – Call ambulance immediately"
    ),

    "chest pain": (
        "Cardiac",
        "Chest pain may occur due to heart, muscle, or gastric problems.\n"
        "Cardiac causes are the most dangerous.",
        "Doctor evaluation is required to identify the cause.\n"
        "Do not ignore chest pain.",
        "• Stop physical activity\n• Sit or lie down",
        "EMERGENCY if pain spreads or increases"
    ),

    "asthma": (
        "Respiratory",
        "Asthma occurs due to airway inflammation and allergy triggers.\n"
        "Dust, smoke, and cold air can worsen it.",
        "Inhalers help open airways.\n"
        "Regular follow-up with doctor is required.",
        "• Avoid dust & smoke\n• Breathing exercises",
        "If severe breathlessness occurs"
    ),

    "acidity": (
        "Digestive",
        "Acidity occurs due to excess stomach acid production.\n"
        "Irregular eating and spicy food worsen it.",
        "Antacids help neutralize acid.\n"
        "Long-term symptoms need medical advice.",
        "• Avoid spicy food\n• Eat small meals",
        "If persistent pain occurs"
    ),

    "diarrhea": (
        "Digestive",
        "Diarrhea occurs due to infection or contaminated food/water.\n"
        "It causes dehydration.",
        "ORS and zinc help restore fluids.\n"
        "Avoid antibiotics unless prescribed.",
        "• Drink plenty of fluids\n• Maintain hygiene",
        "If blood in stool occurs"
    ),

    "back pain": (
        "Musculoskeletal",
        "Back pain occurs due to poor posture, muscle strain, or heavy lifting.\n"
        "Long sitting worsens the condition.",
        "Pain relievers give temporary relief.\n"
        "Physiotherapy helps long-term recovery.",
        "• Hot compress\n• Correct posture\n• Stretching",
        "If pain lasts more than 1 week"
    ),

    "leg pain": (
        "Musculoskeletal",
        "Leg pain occurs due to muscle strain or long standing.\n"
        "Vitamin deficiency may also cause pain.",
        "Pain relievers provide temporary relief.\n"
        "Persistent pain needs evaluation.",
        "• Rest\n• Warm compress\n• Light exercise",
        "If swelling or severe pain occurs"
    ),

    "allergy": (
        "Allergic",
        "Allergy occurs when immune system overreacts to allergens.\n"
        "Dust, pollen, food, or chemicals trigger it.",
        "Antihistamines reduce itching and sneezing.\n"
        "Avoid frequent self-medication.",
        "• Avoid allergens\n• Keep surroundings clean",
        "If swelling or breathing difficulty occurs"
    ),

    "eye irritation": (
        "Eye",
        "Eye irritation occurs due to dust, pollution, or screen overuse.\n"
        "Poor eye hygiene worsens it.",
        "Lubricating eye drops relieve dryness.\n"
        "Avoid random eye medications.",
        "• Wash eyes\n• Reduce screen time",
        "If redness or pain increases"
    ),

    "toothache": (
        "Dental",
        "Toothache occurs due to cavities or gum infection.\n"
        "Poor oral hygiene is the main cause.",
        "Pain relievers provide temporary relief.\n"
        "Dental treatment is required for cure.",
        "• Salt water rinse\n• Avoid sweets",
        "Consult dentist immediately"
    ),

    "migraine": (
        "Neurological",
        "Migraine occurs due to nerve and brain signal changes.\n"
        "Stress and sleep disturbance trigger attacks.",
        "Pain relievers help during mild attacks.\n"
        "Preventive treatment requires doctor advice.",
        "• Rest in dark room\n• Avoid triggers",
        "If frequent or severe attacks occur"
    ),
        # 👩 WOMEN HEALTH
    "urinary tract infection": (
        "Women Health",
        "UTI occurs due to bacterial infection in the urinary tract.\n"
        "Poor hygiene, dehydration, or holding urine can cause it.",
        "Antibiotics are required as prescribed by a doctor.\n"
        "Drink plenty of water.",
        "• Drink more fluids\n• Maintain intimate hygiene\n• Do not hold urine",
        "If burning or fever persists"
    ),

    "vaginal infection": (
        "Women Health",
        "Vaginal infections occur due to bacterial or fungal overgrowth.\n"
        "Hormonal changes and poor hygiene increase risk.",
        "Antifungal or antibiotic treatment may be required.\n"
        "Avoid self-medication.",
        "• Keep area clean and dry\n• Wear cotton underwear",
        "Consult gynecologist if discharge or itching increases"
    ),

    "yeast infection": (
        "Women Health",
        "Yeast infection is caused by fungal overgrowth.\n"
        "It is common during pregnancy or after antibiotics.",
        "Antifungal medicines are used under medical advice.",
        "• Avoid tight clothing\n• Maintain hygiene",
        "If symptoms persist or recur"
    ),

    "pcod": (
        "Women Health",
        "PCOD occurs due to hormonal imbalance affecting ovaries.\n"
        "It can cause irregular periods and weight gain.",
        "Treatment focuses on hormone balance and lifestyle changes.\n"
        "Doctor guidance is essential.",
        "• Healthy diet\n• Regular exercise\n• Weight management",
        "If periods are irregular or painful"
    ),

    "menstrual pain": (
        "Women Health",
        "Menstrual pain occurs due to uterine muscle contractions.\n"
        "Stress and hormonal imbalance can worsen pain.",
        "Pain relievers help reduce cramps.\n"
        "Avoid excessive medication.",
        "• Warm compress\n• Light exercise\n• Adequate rest",
        "If pain is severe or unusual"
    ),

    "irregular periods": (
        "Women Health",
        "Irregular periods occur due to stress, hormonal imbalance, or PCOD.\n"
        "Lifestyle factors play a major role.",
        "Treatment depends on underlying cause.\n"
        "Doctor evaluation is recommended.",
        "• Maintain healthy routine\n• Reduce stress",
        "Consult doctor if cycles are frequently irregular"
    ),
        # 🍽️ DIGESTIVE
    "constipation": (
        "Digestive",
        "Constipation occurs due to low fiber intake, dehydration, or lack of physical activity.\n"
        "Irregular eating habits can worsen the condition.",
        "Fiber supplements or mild laxatives may help.\n"
        "Avoid frequent laxative use without medical advice.",
        "• Eat fiber-rich foods\n• Drink plenty of water\n• Regular physical activity",
        "If constipation lasts more than 1 week"
    ),

    # 🦴 METABOLIC / JOINT
    "uric acid or gout": (
        "Metabolic / Joint",
        "High uric acid occurs due to excess purine breakdown in the body.\n"
        "When crystals deposit in joints, it causes gout with severe pain and swelling.",
        "Medicines may be required to reduce uric acid levels.\n"
        "Diet control and hydration are very important.",
        "• Avoid red meat, seafood & alcohol\n• Drink plenty of water\n• Maintain healthy weight",
        "If severe joint pain, swelling, or redness occurs"
    )
}
image_db = {
    "fever": "images/fever.jpg",
    "cold": "images/cold.jpg",
    "cough": "images/cough.jpg",
    "back pain": "images/back_pain.jpg",
    "leg pain": "images/leg_pain.jpg",
    "chest pain": "images/chestpain.jpg",
    "eye irritation": "images/eye_irritation.jpg",
    "diabetes":"images/diabetes.jpg",
    "gum bleeding": "images/gum.jpg",
    "toothache": "images/toothache.jpg",
    "migraine": "images/migraine.jpg",
    "allergy": "images/allergy.jpg",
    "irregular periods":"images/periods.jpg",
    "uric acid or gout":"images/uric acid.jpg",
    "heart attack": "images/heart_attack.jpg"
}
# ---------------- DATABASE SETUP ----------------
conn = sqlite3.connect("chat_history.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT,
    user_input TEXT,
    bot_response TEXT
)
""")

conn.commit()

  # 🔁 Symptom aliases
# ---------------- SYMPTOM ALIASES ----------------
symptom_aliases = {
    "fever": ["fever", "high temperature", "temperature"],
    "cold": ["cold", "running nose", "sneezing"],
    "cough": ["cough", "throat irritation"],
    "headache": ["headache", "head pain"],
    "migraine": ["migraine", "severe headache"],
    "acidity": ["acidity", "gas", "heartburn"],
    "vomiting": ["vomiting", "nausea"],
    "diarrhea": ["diarrhea", "loose motion"],
    "chest pain": ["chest pain", "chest discomfort"],
    "heart attack": ["heart attack", "cardiac arrest"],
    "heart failure": ["heart failure", "heart problem"],
    "back pain": ["back pain", "lower back pain", "back ache"],
    "leg pain": ["leg pain", "pain in leg", "leg ache"],
    "allergy": ["allergy", "allergies", "itching", "rashes", "skin allergy"],
    "eye irritation": ["eye pain", "eye irritation", "eye redness"],
    "conjunctivitis": ["conjunctivitis", "pink eye"],
    "toothache": ["tooth pain", "toothache"],
    "gum bleeding": ["gum bleeding", "bleeding gums"],
    "urinary tract infection": ["uti", "urine infection", "burning urination"],
    "vaginal infection": ["vaginal infection", "vaginal itching", "discharge"],
    "yeast infection": ["yeast infection", "fungal infection"],
    "pcod": ["pcod", "pcos", "hormonal imbalance"],
    "menstrual pain": ["period pain", "menstrual pain", "cramps"],
    "irregular periods": ["irregular periods", "missed periods"],
    "constipation": ["constipation", "hard stool", "difficulty passing stool"],
    "uric acid or gout": ["uric acid","gout","gout pain","uric acid problem","joint pain due to uric acid","toe joint pain"],
    "diabetes": ["diabetes","high sugar","high blood sugar","blood sugar","sugar problem","sugar disease","type 2 diabetes","type ii diabetes","frequent urination","excessive thirst","increased hunger","uncontrolled sugar"
    ]
}

# ---------------- SESSION STATE ----------------
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello👋,How can i help you Tell me your symptoms."}
    ]

# ---------------- DISPLAY CHAT ----------------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# ---------------- USER INPUT ----------------
# ---------------- USER INPUT ----------------
user_input = st.chat_input("Type your symptoms in English...")

# ⛔ Stop if no input
if not user_input:
    st.stop()
    # ✅ ADD USER MESSAGE TO CHAT HISTORY
# ✅ SHOW USER MESSAGE IMMEDIATELY
with st.chat_message("user"):
    st.write(user_input)

# ✅ ALSO STORE IT
st.session_state.messages.append(
    {"role": "user", "content": user_input}
)

# ✅ DEFINE text ONCE
text = user_input.lower()

reply = "Please consult a doctor for proper diagnosis."
matched_key = None
kannada_prescription = None

# ---------------- MATCHING LOGIC ----------------
for key, aliases in symptom_aliases.items():
    for word in aliases:
        if word in text and key in medical_db:

            category, cause, medicine, advice, warning = medical_db[key]

            reply = (
                f"🩺 Category: {category}\n\n"
                f"🧠 Why it occurs:\n{cause}\n\n"
                f"💊 Prescription / Treatment:\n{medicine}\n\n"
                f"📝 Lifestyle & Home Care:\n{advice}\n\n"
                f"🚨 Warning:\n{warning}"
            )

            kn_translator = GoogleTranslator(source="en", target="kn")
            kannada_prescription = kn_translator.translate(medicine)

            matched_key = key
            break
    if matched_key:
        break

# ---------------- SAVE TO DATABASE ----------------
cursor.execute(
    "INSERT INTO logs (timestamp, user_input, bot_response) VALUES (?, ?, ?)",
    (
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        user_input,
        reply
    )
)
conn.commit()

# ---------------- SHOW ASSISTANT MESSAGE ----------------
st.session_state.messages.append({"role": "assistant", "content": reply})
with st.chat_message("assistant"):
    st.write(reply)

    # 🖼 Image display
    if matched_key and matched_key in image_db:
        image_path = os.path.join(os.getcwd(), image_db[matched_key])
        if os.path.exists(image_path):
            st.image(
                image_path,
                caption=f"{matched_key.title()} – Reference Image",
                width=350
            )