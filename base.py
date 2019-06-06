from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from threading import Thread
from pynput.keyboard import Key, Listener, Controller
import time
from voice import Voice
# from settings import Options
from selenium.webdriver.chrome.options import Options
from ops import similar

pressed = False
voice = Voice()
keyboard = Controller()


def on_press(key):
    global pressed, voice
    if pressed is False and key == Key.ctrl_r:
        pressed = True
        voice.listen()


def on_release(key):
    global pressed, voice
    if pressed is True:
        time.sleep(2.5)
        voice.stop()
        pressed = False
        return False


numbers = {"one":"1", "two":"2", "three":"3", "four":"4", "five":"5", "six":"6", "seven":"7", "eight":"8", "nine":"9",
                      "to":"2",  "tree":"3",  "for":"4"}

keys = {"space":" "}


class Browser:
    def __init__(self):
        # options = self.set_options()
        # self.driver = webdriver.Chrome(options=options.get())
        options = Options()
        options.add_extension(r'D:\Python\Google Translate.crx')
        self.driver = webdriver.Chrome(options=options)
        self.current_tab = 0
        self.scroll_base_speed = 5
        self.scroll_update_speed = 5
        self.scroll_speed = self.scroll_base_speed
        self.button_map = dict()
        self.input_map = dict()
        self.selected_field = None
        self.caps_lock = False

    '''def set_options(self):
        print("Would you like to edit the settings?")
        options = Options()

        listener = Listener(on_press=on_press, on_release=on_release)
        listener.start()
        listener.join()
        if voice.executed is False:
            voice.executed = True
            print(voice.command)
            if not similar("yes", voice.command):
                return options

        print("Settings: ")
        while True:
            listener = Listener(on_press=on_press, on_release=on_release)
            listener.start()
            listener.join()
            if voice.executed is False:
                voice.executed = True
                print(voice.command)
                if similar("done", voice.command):
                    break
                elif similar("maximized", voice.command):
                    print("Browser will start maximized.")
                    options.add_arg("--start-maximized")
        options.set()
        return options'''

    def open(self, url):
        try:
            self.driver.get("http://" + url)
        except:
            print("Couldn't open " + url)

    '''def close(self):
        for tab in self.driver.window_handles:
            self.driver.switch_to.window(tab)
            self.driver.close()'''

    def quit(self):
        self.driver.quit()

    def search(self, text):
        try:
            elem = self.driver.find_element_by_name("q")
            elem.clear()
            elem.send_keys(text)
            elem.send_keys(Keys.RETURN)
        except:
            print("Couldn't search for " + text)

    def click(self, value):
        try:
            nr_tabs = len(self.driver.window_handles)
            buttons = self.driver.find_elements_by_css_selector("button") + \
                      self.driver.find_elements_by_css_selector("a")
            avg_value = None
            for button in buttons:
                if similar(value, button.text) is True:
                    avg_value = button.text
                    break
            if avg_value is None:
                for button in buttons:
                    if value.lower() in button.text.lower():
                        avg_value = button.text
                        break
            if avg_value is None:
                raise Exception
            self.driver.find_element_by_link_text(avg_value).click()
            if len(self.driver.window_handles) != nr_tabs:
                self.switch_tab()
        except:
            print("Couldn't find button " + value)

    def hover(self, value):
        try:
            buttons = self.driver.find_elements_by_css_selector("button") + \
                      self.driver.find_elements_by_css_selector("a")
            avg_value = None
            for button in buttons:
                if similar(value, button.text) is True:
                    avg_value = button.text
                    break
            if avg_value is None:
                for button in buttons:
                    if value.lower() in button.text.lower():
                        avg_value = button.text
                        break
            if avg_value is None:
                raise Exception
            elem = self.driver.find_element_by_link_text(avg_value)
            action = ActionChains(self.driver).move_to_element(elem)
            action.perform()
        except:
            print("Couldn't hover over " + value)

    def page_down(self):
        time.sleep(.001)
        action = ActionChains(self.driver).send_keys(Keys.PAGE_DOWN)
        action.perform()

    def page_up(self):
        time.sleep(.001)
        action = ActionChains(self.driver).send_keys(Keys.PAGE_UP)
        action.perform()

    def scroll_down(self):
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        sc_height = self.driver.execute_script("return window.pageYOffset")
        while True:
            while sc_height < last_height:
                with Listener(on_press=on_press, on_release=on_release) as listener:
                    time.sleep(0.03)
                    if not listener.running:
                        break
                if similar("stop", voice.command) and voice.executed is False:
                    voice.executed = True
                    self.scroll_speed = self.scroll_base_speed
                    print(voice.command)
                    return
                elif similar("go faster", voice.command) and voice.executed is False:
                    voice.executed = True
                    self.scroll_speed += self.scroll_update_speed
                    print(voice.command, self.scroll_speed)
                elif similar("slow down", voice.command) and voice.executed is False:
                    voice.executed = True
                    if self.scroll_speed > self.scroll_base_speed:
                        self.scroll_speed -= self.scroll_update_speed
                    print(voice.command, self.scroll_speed)
                self.driver.execute_script("window.scrollTo(0, %s)" % sc_height)
                sc_height += self.scroll_speed
                last_height = self.driver.execute_script("return document.body.scrollHeight")
            time.sleep(0.5)
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                self.scroll_speed = self.scroll_base_speed
                return
            last_height = new_height

    def scroll_up(self):
        sc_height = self.driver.execute_script("return window.pageYOffset")
        while sc_height > 0:
            with Listener(on_press=on_press, on_release=on_release) as listener:
                time.sleep(0.03)
                if not listener.running:
                    break
            if similar("stop", voice.command) and voice.executed is False:
                voice.executed = True
                self.scroll_speed = self.scroll_base_speed
                print(voice.command)
                return
            elif similar("go faster", voice.command) and voice.executed is False:
                voice.executed = True
                self.scroll_speed += self.scroll_update_speed
                print(voice.command, self.scroll_speed)
            elif similar("slow down", voice.command) and voice.executed is False:
                voice.executed = True
                if self.scroll_speed > self.scroll_base_speed:
                    self.scroll_speed -= self.scroll_update_speed
                print(voice.command, self.scroll_speed)
            self.driver.execute_script("window.scrollTo(0, %s)" % sc_height)
            sc_height -= self.scroll_speed
        self.scroll_speed = self.scroll_base_speed

    def new_tab(self):
        self.driver.execute_script("window.open('');")
        self.current_tab = len(self.driver.window_handles) - 1
        self.driver.switch_to.window(self.driver.window_handles[self.current_tab])

    def switch_tab(self):
        self.current_tab = (self.current_tab + 1) % len(self.driver.window_handles)
        self.driver.switch_to.window(self.driver.window_handles[self.current_tab])

    def close_tab(self):
        self.driver.close()
        try:
            self.switch_tab()
        except:
            global browser
            browser = Browser()

    def refresh(self):
        self.driver.refresh()

    def back(self):
        self.driver.execute_script("window.history.go(-1)")

    def forward(self):
        self.driver.execute_script("window.history.go(1)")

    def bookmark(self):
        with keyboard.pressed(Key.ctrl):
            keyboard.press('d')
            keyboard.release('d')
        time.sleep(0.01)
        keyboard.press(Key.esc)
        keyboard.release(Key.esc)

    def remove_bookmark(self):
        with keyboard.pressed(Key.ctrl):
            keyboard.press('d')
            keyboard.release('d')
        time.sleep(0.01)
        for index in range(0, 4):
            keyboard.press(Key.tab)
            keyboard.release(Key.tab)
        keyboard.press(Key.enter)
        keyboard.release(Key.enter)

    def save(self):
        with keyboard.pressed(Key.ctrl):
            keyboard.press('s')
            keyboard.release('s')

    def source(self):
        with keyboard.pressed(Key.ctrl):
            keyboard.press('u')
            keyboard.release('u')
        time.sleep(0.01)
        self.switch_tab()

    def translate(self):
        ActionChains(self.driver).context_click().perform()
        for index in range(0, 6):
            keyboard.press(Key.down)
            keyboard.release(Key.down)
        keyboard.press(Key.enter)
        keyboard.release(Key.enter)
        keyboard.press(Key.esc)
        keyboard.release(Key.esc)

    def rename_to(self, text):
        with keyboard.pressed(Key.ctrl):
            keyboard.press('a')
            keyboard.release('a')
        for char in text.replace(' ', ''):
            keyboard.press(char.lower())
            keyboard.release(char.lower())

    def submit(self):
        keyboard.press(Key.enter)
        keyboard.release(Key.enter)

    def cancel(self):
        keyboard.press(Key.esc)
        keyboard.release(Key.esc)

    def find_button(self, value):
        self.button_map = dict()
        buttons = self.driver.find_elements_by_css_selector("button") + \
                  self.driver.find_elements_by_css_selector("a")
        for button in buttons:
            if value.lower() in button.text.lower():
                self.button_map[str(len(self.button_map.keys()) + 1)] = button

        for index in self.button_map:
            print(str(index) + ' - ' + self.button_map[index].text)
            self.driver.execute_script("arguments[0].setAttribute('style','color:white;background-color:red')",
                                       self.button_map[index])
            self.driver.execute_script('arguments[0].innerHTML = "{} {}";'.format(index, self.button_map[index].text),
                                       self.button_map[index])
        if len(self.button_map.keys()) == 0:
            print("Couldn't find button " + value)

    def choose_button(self, value):
        try:
            convert = int(value)
        except:
            try:
                value = numbers[value]
            except:
                pass
        if value in self.button_map:
            nr_tabs = len(self.driver.window_handles)
            self.button_map[value].click()
            self.button_map = dict()
            if len(self.driver.window_handles) != nr_tabs:
                self.switch_tab()
        else:
            print("Button " + value + " is not mapped.")

    def find_input_fields(self):
        self.input_map = dict()
        fields = self.driver.find_elements_by_xpath('//input[not(@type="submit")]')
        for field in fields:
            self.input_map[str(len(self.input_map.keys()) + 1)] = field

        for index in self.input_map:
            print(str(index))
            self.driver.execute_script("arguments[0].setAttribute('type','text')",
                                       self.input_map[index])
            self.driver.execute_script("arguments[0].setAttribute('style','color:white;background-color:red')",
                                       self.input_map[index])
            self.driver.execute_script("arguments[0].setAttribute('value','{}')".format(index),
                                       self.input_map[index])

    def select_input_field(self, value):
        try:
            convert = int(value)
        except:
            try:
                value = numbers[value]
            except:
                pass
        if value in self.input_map:
            self.selected_field = self.input_map[value]
        else:
            print("Input " + value + " is not mapped.")

    def type_text(self, text):
        if self.caps_lock is True:
            text = text.upper()
        else:
            text = text.lower()
        fields = self.driver.find_elements_by_xpath('//input[not(@type="submit")]')
        if self.selected_field in fields:
            if text.lower() in keys:
                self.selected_field.send_keys(keys[text.lower()])
            else:
                self.selected_field.send_keys(text.replace(' ', ''))

    def clear_text(self, positions=None):
        try:
            positions = int(positions)
        except:
            try:
                positions = int(numbers[positions])
            except:
                pass
        fields = self.driver.find_elements_by_xpath('//input[not(@type="submit")]')
        if self.selected_field in fields:
            if positions is None:
                self.selected_field.clear()
            else:
                while positions != 0:
                    positions -= 1
                    keyboard.press(Key.backspace)
                    keyboard.release(Key.backspace)

    def change_caps(self, setter):
        if self.caps_lock is False and setter.lower() == "on":
            self.caps_lock = True
            keyboard.press(Key.caps_lock)
            keyboard.release(Key.caps_lock)
        elif self.caps_lock is True and setter.lower() == "off":
            self.caps_lock = False
            keyboard.press(Key.caps_lock)
            keyboard.release(Key.caps_lock)


browser = Browser()

#TODO form completion
#TODO map all clickables on page (and input fields)
#TODO fix translate


if __name__ == '__main__':
    # browser.open('python.org')
    # browser.close()
    # browser.search('gigel')
    # browser.click('Downloads')
    # browser.hover('About')
    # browser.find_form_fields()
    # browser.fill_form_field('_user', 'USERNAME')
    # browser.fill_form_field('_pass', 'PASSWORD', submit=True)
    # browser.scroll_down()
    # browser.new_tab()
    # browser.open('webmail-studs.info.uaic.ro/')
    # browser.switch_tab()
    # browser.close_tab()
    # browser.back()

    # thread = Thread(target=voice.listen)
    # thread.daemon = True
    # thread.start()
    while True:
        listener = Listener(on_press=on_press, on_release=on_release)
        listener.start()
        listener.join()
        if voice.executed is False:
            voice.executed = True
            print(voice.command)

            if similar("go to", " ".join(voice.command.split()[:2])):
                url = " ".join(voice.command.split()[2:])
                browser.open(url)

            elif similar("search", " ".join(voice.command.split()[:1])):
                text = " ".join(voice.command.split()[1:])
                browser.search(text)

            elif similar("click on", " ".join(voice.command.split()[:2])):
                value = " ".join(voice.command.split()[2:])
                browser.click(value)

            elif similar("hover on", " ".join(voice.command.split()[:2])):
                value = " ".join(voice.command.split()[2:])
                browser.hover(value)

            elif similar("page down", voice.command):
                browser.page_down()

            elif similar("page up", voice.command):
                browser.page_up()

            elif similar("scroll down", voice.command):
                browser.scroll_down()

            elif similar("scroll up", voice.command):
                browser.scroll_up()

            elif similar("open new tab", voice.command):
                browser.new_tab()

            elif similar("switch tab", voice.command):
                browser.switch_tab()

            elif similar("close tab", voice.command):
                browser.close_tab()

            elif similar("refresh", voice.command):
                browser.refresh()

            elif similar("go back", voice.command):
                browser.back()

            elif similar("go forward", voice.command):
                browser.forward()

            elif similar("bookmark", voice.command) and "remove" not in voice.command:
                browser.bookmark()

            elif similar("remove bookmark", voice.command):
                browser.remove_bookmark()

            elif similar("translate", voice.command):
                browser.translate()

            elif similar("save", voice.command):
                browser.save()

            elif similar("view page source", voice.command):
                browser.source()

            elif similar("rename to", " ".join(voice.command.split()[:2])):
                text = " ".join(voice.command.split()[2:])
                browser.rename_to(text)

            elif similar("submit", voice.command):
                browser.submit()

            elif similar("cancel", voice.command):
                browser.cancel()

            elif similar("find the button", " ".join(voice.command.split()[:3])):
                value = " ".join(voice.command.split()[3:])
                browser.find_button(value)

            elif similar("choose button number", " ".join(voice.command.split()[:3])):
                value = " ".join(voice.command.split()[3:])
                browser.choose_button(value)

            elif similar("find input fields", voice.command):
                browser.find_input_fields()

            elif similar("select input field", " ".join(voice.command.split()[:3])):
                value = voice.command.split()[3]
                browser.select_input_field(value)

            elif similar("type text", " ".join(voice.command.split()[:2])):
                text = " ".join(voice.command.split()[2:])
                browser.type_text(text)

            elif similar("clear", voice.command.split()[0]):
                try:
                    positions = voice.command.split()[1]
                    browser.clear_text(positions)
                except:
                    browser.clear_text()

            elif similar("caps", voice.command.split()[0]):
                setter = voice.command.split()[1]
                browser.change_caps(setter)

            elif voice.command == "exit":
                browser.quit()
                break
