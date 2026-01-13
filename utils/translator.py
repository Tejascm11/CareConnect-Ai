from deep_translator import GoogleTranslator

def translate_to_kannada(text):
    try:
        translator = GoogleTranslator(source="en", target="kn")
        return translator.translate(text)
    except:
        return None