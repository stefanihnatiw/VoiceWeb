from selenium import webdriver


class Options:
    def __init__(self):
        self.chromeOptions = webdriver.ChromeOptions()
        self.prefs = dict()

    def add_key(self, key, value):
        self.prefs[key] = value

    def add_arg(self, arg):
        self.chromeOptions.add_argument(arg)

    def set(self):
        self.chromeOptions.add_experimental_option("prefs", self.prefs)

    def get(self):
        return self.chromeOptions
