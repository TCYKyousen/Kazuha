from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtCore import QUrl
import os
import win32com.client

class SoundManager:
    def __init__(self, resource_dir):
        self.resource_dir = resource_dir
        self.players = {}
        self.outputs = {}
        try:
            self.speaker = win32com.client.Dispatch("SAPI.SpVoice")
        except:
            self.speaker = None

    def play(self, sound_name, loop=False, custom_path=None):
        """
        Play a sound effect.
        :param sound_name: The name of the sound file (e.g., 'Switch' or 'Switch.ogg')
        :param loop: Whether to loop the sound
        :param custom_path: Optional absolute path to override resource_dir
        """
        if custom_path:
            full_path = custom_path
            key = custom_path
        else:
            filename = sound_name if sound_name.endswith('.ogg') else f"{sound_name}.ogg"
            full_path = os.path.join(self.resource_dir, filename)
            key = filename
        
        if key not in self.players:
            if os.path.exists(full_path):
                player = QMediaPlayer()
                audio_output = QAudioOutput()
                player.setAudioOutput(audio_output)
                player.setSource(QUrl.fromLocalFile(full_path))
                self.players[key] = player
                self.outputs[key] = audio_output
            else:
                print(f"Sound file not found: {full_path}")
                return

        player = self.players[key]
        if player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            player.stop()
            
        if loop:
            player.setLoops(QMediaPlayer.Loops.Infinite)
        else:
            player.setLoops(1)
            
        player.play()

    def stop(self, sound_name, custom_path=None):
        if custom_path:
            key = custom_path
        else:
            key = sound_name if sound_name.endswith('.ogg') else f"{sound_name}.ogg"
            
        if key in self.players:
            self.players[key].stop()

    def speak(self, text):
        if self.speaker:
            try:
                # 1 = SVSFlagsAsync
                self.speaker.Speak(text, 1)
            except Exception as e:
                print(f"TTS Error: {e}")
