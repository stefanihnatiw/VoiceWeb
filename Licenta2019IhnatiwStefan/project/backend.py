from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from pynput.keyboard import Key, Listener, Controller
import urllib.parse
import time
from selenium.webdriver.chrome.options import Options
import speech_recognition as sr
import re, Levenshtein


def similar(s1, s2):
    s1 = re.sub("[^A-Za-z]", "", s1).lower()
    s2 = re.sub("[^A-Za-z]", "", s2).lower()
    if s1 == s2 or Levenshtein.ratio(s1, s2) > 0.9:
        return True
    return False


class Voice:
    def __init__(self):
        self.command = ""
        self.executed = False
        self.stop_listening = None

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

keys = {"space":" ", "slash":"/", "backslash":"\\", "open brackets":"(", "close brackets":")", "plus":"+", "minus":"-",
        "underscore":"_", "comma":",", "dot":".", "quote":"\"", "question mark":"?", "exclamation mark":"!"}


class Browser:
    def __init__(self):
        options = Options()
        options.add_experimental_option("debuggerAddress", "localhost:9014")
        self.driver = webdriver.Chrome(options=options)
        self.current_tab = 0
        self.scroll_base_speed = 5
        self.scroll_update_speed = 5
        self.scroll_speed = self.scroll_base_speed
        self.button_map = dict()
        self.input_map = dict()
        self.image_map = dict()
        self.selected_field = None
        self.caps_lock = False
        self.copied_text = None

    def open(self, url):
        try:
            self.driver.get("http://" + url)
        except:
            print("Couldn't open " + url)

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
                      self.driver.find_elements_by_css_selector("a") + \
                      self.driver.find_elements_by_xpath('//input[@type="submit"]')
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
                      self.driver.find_elements_by_css_selector("a") + \
                      self.driver.find_elements_by_xpath('//input[@type="submit"]')
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
        keyboard.press(Key.page_down)
        keyboard.release(Key.page_down)

    def page_up(self):
        keyboard.press(Key.page_up)
        keyboard.release(Key.page_up)

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
            browser.quit()

    def refresh(self):
        self.driver.refresh()

    def back(self):
        try:
            self.driver.execute_script("window.history.go(-1)")
        except:
            print("Couldn't perform the operation.")

    def forward(self):
        try:
            self.driver.execute_script("window.history.go(1)")
        except:
            print("Couldn't perform the operation.")

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
        time.sleep(0.1)
        self.switch_tab()

    def submit(self):
        keyboard.press(Key.enter)
        keyboard.release(Key.enter)

    def cancel(self):
        keyboard.press(Key.esc)
        keyboard.release(Key.esc)

    def find_button(self, value=''):
        self.button_map = dict()
        buttons = self.driver.find_elements_by_css_selector("button") + \
                  self.driver.find_elements_by_css_selector("a") + \
                  self.driver.find_elements_by_xpath('//input[@type="submit"]')
        for button in buttons:
            if value == '' or value.lower() in button.text.lower():
                self.button_map[str(len(self.button_map.keys()) + 1)] = button

        for index in self.button_map:
            print(str(index) + ' - ' + self.button_map[index].text)
            try:
                script = '''
                         var node = document.createElement("div");
                         var textnode = document.createTextNode("{}");
                         node.appendChild(textnode);
                         node.setAttribute('style', 'position:relative;left:10px;display:table-cell;border-radius:20px;font-size:1.5em;background-color:red;color:white');
                         '''.format(index)
                if self.button_map[index].tag_name == 'input':
                    self.driver.execute_script(script + 'arguments[0].parentNode.appendChild(node);', self.button_map[index])
                else:
                    self.driver.execute_script(script + 'arguments[0].appendChild(node);', self.button_map[index])
            except Exception as e:
                print(e)
                pass
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
            try:
                nr_tabs = len(self.driver.window_handles)
                self.button_map[value].click()
                self.button_map = dict()
                if len(self.driver.window_handles) != nr_tabs:
                    self.switch_tab()
            except Exception as e:
                print("Element not interactable.")
        else:
            print("Button " + value + " is not mapped.")

    def hover_button(self, value):
        try:
            convert = int(value)
        except:
            try:
                value = numbers[value]
            except:
                pass
        if value in self.button_map:
            try:
                action = ActionChains(self.driver).move_to_element(self.button_map[value])
                action.perform()
            except Exception as e:
                print("Element not interactable.")
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
            self.selected_field.clear()
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

    def find_images(self):
        self.image_map = dict()
        images = self.driver.find_elements_by_css_selector("img")
        for image in images:
            self.image_map[str(len(self.image_map.keys()) + 1)] = image

        for index in self.image_map:
            print(str(index))
            self.driver.execute_script('''
                                       var node = document.createElement("div");
                                       var textnode = document.createTextNode("{}");
                                       node.appendChild(textnode);
                                       node.setAttribute('style', 'position:relative;left:10px;display:table-cell;border-radius:20px;font-size:1.5em;background-color:red;color:white');
                                       arguments[0].parentNode.appendChild(node);
                                       '''.format(index), self.image_map[index])

    def select_image(self, value):
        try:
            convert = int(value)
        except:
            try:
                value = numbers[value]
            except:
                pass
        if value in self.image_map:
            try:
                src = self.driver.execute_script("return arguments[0].getAttribute('src')", self.image_map[value])
                if src[0:2] == "//":
                    self.open(src)
                else:
                    self.open(self.driver.current_url[6:] + src)
            except Exception as e:
                print(e)
        else:
            print("Input " + value + " is not mapped.")

    def change_caps(self, setter):
        if self.caps_lock is False and setter.lower() == "on":
            self.caps_lock = True
            keyboard.press(Key.caps_lock)
            keyboard.release(Key.caps_lock)
        elif self.caps_lock is True and setter.lower() == "off":
            self.caps_lock = False
            keyboard.press(Key.caps_lock)
            keyboard.release(Key.caps_lock)

    def translate(self):
        with keyboard.pressed(Key.ctrl):
            keyboard.press('q')
            keyboard.release('q')
        time.sleep(0.1)
        keyboard.press(Key.tab)
        keyboard.release(Key.tab)
        keyboard.press(Key.tab)
        keyboard.release(Key.tab)
        keyboard.press(Key.enter)
        keyboard.release(Key.enter)
        '''
        url = "translate.google.com/translate?hl=en&sl=auto&tl=en&u=" + \
              urllib.parse.quote(self.driver.current_url, safe='')
        self.open(url)
        time.sleep(3)
        self.driver.switch_to.default_content()
        iframe = self.driver.find_element_by_tag_name('iframe')
        self.driver.execute_script("arguments[0].setAttribute('id','iframe_id')",
                                   iframe)
        self.driver.switch_to.frame('iframe_id')
        print(self.driver.find_element_by_xpath("//div").get_attribute('id'))
        '''

    def look_for(self, text):
        with keyboard.pressed(Key.ctrl):
            keyboard.press('f')
            keyboard.release('f')
        time.sleep(0.01)
        for ch in text.lower():
            keyboard.press(ch)
            keyboard.release(ch)

    def undo(self):
        with keyboard.pressed(Key.ctrl):
            keyboard.press('z')
            keyboard.release('z')

    def redo(self):
        with keyboard.pressed(Key.ctrl):
            with keyboard.pressed(Key.shift):
                keyboard.press('z')
                keyboard.release('z')

    def select_text(self, text):
        try:
            elems = self.driver.find_elements_by_css_selector("*")
            for elem in elems:
                if text.lower() in elem.text.lower() and len(elem.find_elements_by_css_selector(":not(a):not(b):not(i)")) == 0:
                    self.copied_text = elem.text
                    self.driver.execute_script("arguments[0].setAttribute('style','color:white;background-color:red')",
                                               elem)
                    return
            print("Text couldn't be found.")
        except:
            print("Text couldn't be found.")

    def paste(self):
        fields = self.driver.find_elements_by_xpath('//input[not(@type="submit")]')
        if self.selected_field in fields and self.copied_text is not None:
            self.selected_field.send_keys(self.copied_text)

    def view_bookmarks(self):
        with keyboard.pressed(Key.ctrl):
            with keyboard.pressed(Key.shift):
                keyboard.press('o')
                keyboard.release('o')
        time.sleep(0.01)
        self.switch_tab()

    def select_bookmark(self, value):

        def get_shadow(element):
            return self.driver.execute_script('return arguments[0].shadowRoot', element)

        try:
            bookmarks_app = self.driver.find_element_by_css_selector("bookmarks-app")
            shadow_root = get_shadow(bookmarks_app)
            bookmarks_list = shadow_root.find_element_by_css_selector("div bookmarks-list")
            shadow_root = get_shadow(bookmarks_list)
            bookmarks = shadow_root.find_elements_by_css_selector("iron-list bookmarks-item")
            for bookmark in bookmarks:
                shadow_root = get_shadow(bookmark)
                title = shadow_root.find_element_by_css_selector("#website-title").get_attribute('title')
                url = shadow_root.find_element_by_css_selector("#website-url").get_attribute('title')
                if value.lower() in title.lower():
                    self.driver.get(url)
                    return
        except:
            print("Couldn't find the specified bookmark.")


browser = Browser()


def start():
    browser.open('google.com')
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

            elif similar("save", voice.command):
                browser.save()

            elif similar("view page source", voice.command):
                browser.source()

            elif similar("submit", voice.command) or similar("next", voice.command):
                browser.submit()

            elif similar("cancel", voice.command):
                browser.cancel()

            elif similar("find the button", " ".join(voice.command.split()[:3])):
                value = " ".join(voice.command.split()[3:])
                browser.find_button(value)

            elif similar("find all buttons", voice.command):
                browser.find_button()

            elif similar("choose button number", " ".join(voice.command.split()[:3])):
                value = " ".join(voice.command.split()[3:])
                browser.choose_button(value)

            elif similar("hover button number", " ".join(voice.command.split()[:3])):
                value = " ".join(voice.command.split()[3:])
                browser.hover_button(value)

            elif similar("find input fields", voice.command):
                browser.find_input_fields()

            elif similar("select input field", " ".join(voice.command.split()[:3])):
                value = voice.command.split()[3]
                browser.select_input_field(value)

            elif similar("type text", " ".join(voice.command.split()[:2])):
                text = " ".join(voice.command.split()[2:])
                browser.type_text(text)

            elif len(voice.command.split()) >= 1 and voice.command.split()[0] == "clear":
                try:
                    positions = voice.command.split()[1]
                    browser.clear_text(positions)
                except:
                    try:
                        browser.clear_text()
                    except:
                        pass

            elif similar("find images", voice.command):
                browser.find_images()

            elif similar("select image", " ".join(voice.command.split()[:2])):
                value = voice.command.split()[2]
                browser.select_image(value)

            elif len(voice.command.split()) == 2 and voice.command.split()[0] == "caps":
                setter = voice.command.split()[1]
                browser.change_caps(setter)

            elif similar("translate", voice.command):
                browser.translate()

            elif similar("look for", " ".join(voice.command.split()[:2])):
                text = " ".join(voice.command.split()[2:])
                browser.look_for(text)

            elif similar("undo", voice.command):
                browser.undo()

            elif similar("redo", voice.command):
                browser.redo()

            elif similar("select text", " ".join(voice.command.split()[:2])):
                text = " ".join(voice.command.split()[2:])
                browser.select_text(text)

            elif similar("paste text", voice.command):
                browser.paste()

            elif similar("view bookmarks", voice.command):
                browser.view_bookmarks()

            elif similar("select bookmark", " ".join(voice.command.split()[:2])):
                value = " ".join(voice.command.split()[2:])
                browser.select_bookmark(value)

            elif voice.command == "exit":
                browser.quit()
                break

            else:
                print("Say that again, please.")
