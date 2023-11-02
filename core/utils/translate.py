from googletrans import Translator


def translate(text_input):
    translator = Translator()
    try:
        translation = translator.translate(text_input, dest='ru').text
    except Exception as e:
        print(f'Error while translate: {e}')
        translation = text_input
    return translation
