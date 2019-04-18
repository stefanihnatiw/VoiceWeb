import speech_recognition as sr


# class Voice:
#     def __init__(self):
#         self.command = ""
#         self.executed = True
#         # with sr.Microphone() as source:
#         #     print("Please wait. Calibrating microphone...")
#         #     sr.Recognizer().adjust_for_ambient_noise(source)
#
#     def listen(self):
#         while True:
#             r = sr.Recognizer()
#             with sr.Microphone() as source:
#                 print("Say something!")
#                 audio = r.listen(source)
#             try:
#                 self.command = r.recognize_google(audio)
#                 self.executed = False
#             except sr.UnknownValueError:
#                 self.command = "?!?"
#             except sr.RequestError as e:
#                 self.command = "Could not request results from Google Speech Recognition service; {0}".format(e)


class Voice:
    def __init__(self):
        self.command = ""
        self.executed = False
        self.stop_listening = None
        # with sr.Microphone() as source:
        #     print("Please wait. Calibrating microphone...")
        #     sr.Recognizer().adjust_for_ambient_noise(source)

    def recognize(self, r, audio):
        try:
            self.command = r.recognize_google(audio)
            self.executed = False
        except sr.UnknownValueError:
            self.command = "?!?"
        except sr.RequestError as e:
            self.command = "Could not request results from Google Speech Recognition service; {0}".format(e)

    def listen(self):
        r = sr.Recognizer()
        m = sr.Microphone()
        print("Say something!")
        self.stop_listening = r.listen_in_background(m, self.recognize)

    def stop(self):
        self.stop_listening(wait_for_stop=False)
