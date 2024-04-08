from PyQt5.QtCore import QSize, QThread, QUrl
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QPushButton,
    QHBoxLayout,
    QVBoxLayout,
    QLineEdit,
    QLabel,
)
from PyQt5.QtGui import QIcon
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget
from colorama import init, Fore, Style
from pydantic_core import Url

from llm.gemini import Gemini
from llm.gemini_langchain import LangchainChat
from listener import AudioListener, TTS


class AvatarWidget(QWidget):
    def __init__(self, controller):
        super(AvatarWidget, self).__init__(controller)
        self.loop_count = 0
        self.controller = controller
        # create a layout
        self.layout = QVBoxLayout()
        # create video widget
        self.video_widget = QVideoWidget()
        self.layout.addWidget(self.video_widget)
        self.setFixedSize(QSize(600, 800))
        # create a media player
        self.media_player = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        self.media_player.setVideoOutput(self.video_widget)
        # mute audio
        self.media_player.setMuted(False)
        # Set up a video file
        # self.media_player.stateChanged.connect(self.loop_video)
        self.setLayout(self.layout)
        self.show()

    def play_video(self):
        if self.media_player.state() == QMediaPlayer.PlayingState:
            # stop currently playing video
            self.stop_video()

        self.media_content = QMediaContent(QUrl.fromLocalFile("output.mp4"))
        self.media_player.setMedia(self.media_content)

        self.media_player.play()

    def stop_video(self):
        self.media_player.stop()
        self.media_player.setMedia(QMediaContent())


class VirtualAssistantApp(QMainWindow):
    def __init__(self):
        super(VirtualAssistantApp, self).__init__()
        self.setFixedHeight(1000)
        self.init_gemini()
        self.init_listener()
        self.avatar_widget = AvatarWidget(self)

        layout = QVBoxLayout()
        self.talk_btn = QPushButton()
        icon = QIcon("./icons/microphone.png")
        self.talk_btn.setIcon(icon)
        self.talk_btn.setIconSize(QSize(64, 64))
        self.talk_btn.clicked.connect(self.listen_action)

        layout.addWidget(self.avatar_widget)
        layout.addWidget(self.talk_btn)

        widget = QWidget()
        widget.setLayout(layout)

        self.setCentralWidget(widget)

    def init_listener(self):
        self.listener = AudioListener()

    def init_gemini(self):
        self.gemini = LangchainChat()  # Gemini()

    def listen_action(self):
        self.talk_btn.setEnabled(False)

        prompt = self.listener.listen_prompt()

        if any(keyword == prompt for keyword in ["stop", "enough"]):
            # Kill the thread response thread
            if self.tts_thread:
                self.stop_tts_thread()
                self.avatar_widget.stop_video()
                self.talk_btn.setEnabled(True)
                return

        if prompt:
            gemini_response = self.gemini.get_response(prompt).replace("*", "")
            print(Fore.YELLOW + "Assitant:>")
            print(gemini_response)
        self.update()

        self.tts_thread = QThread()
        self.tts = TTS(gemini_response)
        self.tts.moveToThread(self.tts_thread)

        self.tts_thread.started.connect(self.tts.run)
        # self.tts_thread.started.connect(self.avatar_widget.play_video)

        self.tts.process_complete.connect(self.stop_tts_thread)
        self.tts.process_complete.connect(self.avatar_widget.play_video)

        self.tts_thread.start()

        return

    def stop_tts_thread(self):
        self.tts_thread.quit()
        self.tts_thread.wait()
        self.talk_btn.setEnabled(True)

    def update_text(self):
        # print(len(self.text.rstrip().split("\n")))
        self.textbox.setText(self.text)
        self.update()
        return


app = QApplication([])
window = VirtualAssistantApp()
# window = AvatarWidget(None)
window.show()
app.exec()
