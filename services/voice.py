def generate_speech(text, api_key=None):
    """
    Render no permite TTS local, así que delegamos la voz al navegador.
    Esta función solo devuelve el texto recibido.
    """
    return {"text": text}
