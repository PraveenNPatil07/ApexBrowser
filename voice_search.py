import speech_recognition as sr

def voice_search():
    """Capture voice input and return the transcribed text"""
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening for voice input...")
        try:
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)
            query = recognizer.recognize_google(audio)
            print(f"Voice search query: {query}")
            return query
        except sr.UnknownValueError:
            print("Could not understand the audio")
            return None
        except sr.RequestError as e:
            print(f"Voice recognition error: {e}")
            return None
        except Exception as e:
            print(f"Error during voice search: {e}")
            return None
