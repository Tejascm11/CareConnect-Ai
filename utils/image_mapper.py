import os

def get_image_for_symptom(user_input, image_dir="images"):
    IMAGE_MAP = {
        "fever": "fever.jpg",
        "cold": "cold.jpg",
        "cough": "cough.jpg",
        "back pain": "back_pain.jpg",
        "leg pain": "leg_pain.jpg",
        "chest pain": "chestpain.jpg",
        "eye irritation": "eye_irritation.jpg",
        "diabetes":"diabetes.jpg",
        "gum bleeding": "gum.jpg",
        "toothache": "toothache.jpg",
        "migraine": "migraine.jpg",
        "allergy": "allergy.jpg",
        "irregular periods":"periods.jpg",
        "uric acid or gout":"uric acid.jpg",
        "heart attack": "heart_attack.jpg"
    }
    text = user_input.lower()

    for keyword, image_name in IMAGE_MAP.items():
        if keyword in text:
            path = os.path.join(image_dir, image_name)
            if os.path.exists(path):
                return path

    default_path = os.path.join(image_dir, "default.jpg")
    if os.path.exists(default_path):
        return default_path

    return None