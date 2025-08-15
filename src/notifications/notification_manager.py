import logging
import threading
import pyttsx3

try:
    import winsound
    IS_WINDOWS = True
except ImportError:
    IS_WINDOWS = False
    logging.warning("winsound module not found. Beep notifications will not be available.")

class NotificationManager:
    def __init__(self):
        self.engine = None
        self.voice_id = None
        self.engine_lock = threading.Lock()
        try:
            self._initialize_engine()
        except Exception as e:
            logging.error(f"Failed to set up voice notification system: {e}")

    def _initialize_engine(self):
        try:
            with self.engine_lock:
                self.engine = pyttsx3.init()
                voices = self.engine.getProperty('voices')
                # Prioritize female voices
                for voice in voices:
                    if 'female' in voice.name.lower() or 'zira' in voice.name.lower():
                        self.voice_id = voice.id
                        break
                if not self.voice_id and voices:
                    self.voice_id = voices[0].id

                if self.voice_id:
                    self.engine.setProperty('voice', self.voice_id)

                self.engine.setProperty('rate', 150)
                self.engine.setProperty('volume', 1.0)
                logging.info("Voice notification system ready.")
        except Exception as e:
            logging.error(f"Could not initialize pyttsx3 engine: {e}")
            self.engine = None

    def play_notification_sound(self, sound_type="default"):
        if not IS_WINDOWS:
            print("\a", flush=True) # Bell character for non-windows
            return
        try:
            if sound_type == "long":
                winsound.Beep(1200, 500)
            elif sound_type == "short":
                winsound.Beep(800, 500)
            else:
                winsound.Beep(1000, 500)
        except Exception as e:
            logging.error(f"Failed to play notification sound: {e}")

    def speak_notification(self, text):
        def speak_thread():
            with self.engine_lock:
                if not self.engine:
                    logging.warning("Speech engine not available.")
                    return
                try:
                    self.engine.say(text)
                    self.engine.runAndWait()
                except Exception as e:
                    logging.error(f"Error during speech: {e}")

        thread = threading.Thread(target=speak_thread)
        thread.daemon = True
        thread.start()

    def notify_trade(self, direction, pair):
        self.play_notification_sound(sound_type=direction)
        formatted_pair = pair.replace('/', ' ')

        if direction.lower() == "long":
            notification_text = f"Long trade taken in {formatted_pair}."
        elif direction.lower() == "short":
            notification_text = f"Short trade taken in {formatted_pair}."
        else:
            notification_text = f"Trade {direction} taken in {formatted_pair}"

        self.speak_notification(notification_text)
        logging.info(f"Trade notification: {notification_text}")
