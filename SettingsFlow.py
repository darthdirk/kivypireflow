# gf
import time, sys, io, serial, json, requests, pickle, os, subprocess
import platform
from kivy.config import Config
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager, Screen


class SettingsPage(Screen):
    def __init__(self, **kwargs):
        Screen.__init__(self, **kwargs)

    def on_pre_enter(self):
        self.manager.parent.show_buttons()
        self.get_ip()
        self.get_git()

    def on_enter(self):
        self.ids["test_checkbox"].bind(active=self.on_test_active)
        self.ids["no_login_checkbox"].bind(active=self.on_no_login_active)

    def on_pre_leave(self):
        self.save_settings()

    def on_leave(self):
        self.manager.parent.ids["main"].REFRESH = True

    def on_test_active(self, instance, isActive):
        self.ids["no_login_checkbox"].active = not isActive

    def on_no_login_active(self, instance, isActive):
        self.ids["test_checkbox"].active = not isActive
        if isActive:
            self.ids["touchscreen_checkbox"].active = True
            for i in ["oven"]:
                self.manager.part_class.append(i)
            for i in ["U", "IP", "C", "WS", "FM"]:
                self.ids["{}_checkbox".format(i)].active = False

    def get_ip(self):
        if platform.system() == 'Linux':
            cmd = """ip -o addr | awk '!/^[0-9]*: ?lo|link\/ether/ {gsub("/", " "); print $4", "}' | grep -v :"""
        elif platform.system() == 'Darwin':
            cmd = """ifconfig | grep -E 'inet[^6]' | grep -v '127.0.0.1' | awk '{print $2}'"""

        self.manager.ip = os.popen(cmd).read().replace('\n', '').rstrip(', ')

    def get_git(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.manager.git = os.popen("""cd {} && git describe --always""".format(current_dir)).read().replace('\n', '')

    # Returns IP address or ID of server depending on input
    def get_server(self, ip=None):
        if ip == None:
            if self.ids["fabrication_checkbox"].active:
                backend_ip = self.manager.server_list["production_checkbox"]
            elif self.ids["testing_checkbox"].active:
                backend_ip = self.manager.server_list["testing_checkbox"]
            else:
                backend_ip = self.manager.backend_server
            return backend_ip

        else:
            for id, server_ip in self.manager.server_list.items():
                if ip == server_ip:
                    return id

    def load_settings(self):
        config = None
        try:
            config = pickle.load(open("Kiflow.conf", 'rb'))
        except:
            pass  # Failed to load configuration

        if config is not None:
            self.manager.station = config["station"]
            self.manager.part_class = config["pcb_size"]

            if not os.environ.get('DEBUG_KIVY') and "armv7l" in platform.machine():
                try:
                    os.system(
                        "sudo hostnamectl set-hostname oven-{}-{}".format(self.manager.facility, self.manager.station))
                except Exception as e:
                    print(e)

            try:
                self.manager.test_station = config["test_station"]
                self.ids["test_checkbox"].active = self.manager.test_station
                # Convert IP to ID for checkbox
                self.ids[
                    self.get_server(self.manager.backend_server)
                ].active = True
                self.manager.no_login_station = config["no_login_station"]
                self.ids["no_login_checkbox"].active = self.manager.no_login_station
                self.manager.touchscreen = config["touchscreen"]
                self.ids["touchscreen_checkbox"].active = self.manager.touchscreen
                self.manager.backend_server = config["backend_server"]
            except Exception as e:
                print(e)  # Failed to load something in settings

            for i in self.manager.part_class:
                try:
                    self.ids["{}_checkbox".format(i)].active = True
                except Exception as e:
                    print(e)  # Failed to load something in settings

            if not self.manager.touchscreen:
                Config.set('input', 'mouse', 'mouse,disable_on_activity')
                Config.set('graphics', 'show_cursor', 0)
                Config.set('modules', 'touchring', 'show_cursor=False')
                Config.write()
                Window.show_cursor = True
                if "armv7l" in platform.machine():
                    subprocess.call(["sed", "-i", "/^cursor/d", "/home/pi/.kivy/config.ini"])
                    subprocess.call(["sed", "-i", "/^mtdev_/d", "/home/pi/.kivy/config.ini"])
                    subprocess.call(["sed", "-i", "/^hid_/d", "/home/pi/.kivy/config.ini"])
            else:
                Config.set('input', 'mouse', 'mouse')
                Config.set('graphics', 'show_cursor', 0)
                Config.set('modules', 'touchring', 'show_cursor=False')
                Config.set('input', 'mtdev_%(name)s', 'probesysfs,provider=mtdev')
                Config.set('input', 'hid_%(name)s', 'probesysfs,provider=hidinput')
                Config.write()
                Window.show_cursor = False
                Window.mouse_pos = [9999, 9999]

    def save_settings(self):
        self.manager.station = int(self.ids["station_input"].text)
        self.manager.test_station = bool(self.ids["test_checkbox"].active)
        self.manager.backend_server = self.get_server()
        self.manager.no_login_station = bool(self.ids["no_login_checkbox"].active)
        self.manager.touchscreen = bool(self.ids["touchscreen_checkbox"].active)
        self.manager.part_class = []

        config = {
            "facility": self.manager.facility,
            "station": self.manager.station,
            "test_station": self.manager.test_station,
            "touchscreen": self.manager.touchscreen,
            "no_login_station": self.manager.no_login_station,
            "pcb_size": list(self.manager.pcb_size),
            "backend_server": self.manager.backend_server,
        }
        try:
            pickle.dump(config, open("oven.conf", 'wb'))
        except Exception as e:
            print(e)  # Failed to save the settings