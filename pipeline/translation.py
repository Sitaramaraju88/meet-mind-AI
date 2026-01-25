from googletrans import Translator  # lightweight translation library

translator = Translator()

def translate_segments(segments, target_lang="hi"):
    """
    Translate segmented transcript into target language.
    
    Args:
        segments (list): List of dictionaries with keys 'speaker', 'start', 'end', 'text'
        target_lang (str): Target language code (e.g., 'hi' for Hindi)
    
    Returns:
        list: Same structure, with translated 'text'
    """
    translated = []
    for seg in segments:
        translated_text = translator.translate(seg['text'], dest=target_lang).text
        translated.append({
            "speaker": seg['speaker'],
            "start": seg['start'],
            "end": seg['end'],
            "text": translated_text
        })
    return translated
