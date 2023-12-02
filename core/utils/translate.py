from deep_translator import GoogleTranslator


def translate(text_input):
    translator = GoogleTranslator(target='russian')
    if not text_input:
        return text_input
    try:
        translation = translator.translate(text_input)
    except Exception as e:
        print(f'Error while translate: {e}')
        translation = text_input
    return translation
