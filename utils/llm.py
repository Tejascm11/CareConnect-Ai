from groq import Groq

client = Groq(api_key="YOUR_GROQ_API_KEY")

def get_medical_response(user_input):
    prompt = f"""
You are CareConnect, a responsible medical assistant.

IMPORTANT RULES:
- Do NOT diagnose diseases
- Do NOT prescribe antibiotics or strong medicines
- Give ONLY general medical advice and OTC prescriptions
- Use simple English
- Be clear and reassuring
- Always suggest consulting a doctor if symptoms persist or worsen

Response format:
1. Explanation of the health problem
2. Common reasons for the problem
3. General medical prescription (OTC only)
4. Home care and lifestyle advice
5. Safety warning / when to see a doctor

Allowed medicine examples:
- Paracetamol
- ORS
- Antacids
- Pain relief gel
- Steam inhalation

User symptoms:
{user_input}
"""

    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        return response.choices[0].message.content

    except Exception as e:
        return (
            "Sorry, I am unable to provide medical advice right now. "
            "Please consult a healthcare professional."
        )