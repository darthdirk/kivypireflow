# gf
import time, sys, io, serial, json, requests, os, datetime
from threading import Thread
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.graphics import Canvas, Color, Rectangle, InstructionGroup
from kivy.uix.spinner import Spinner, SpinnerOption
from kivy.uix.dropdown import DropDown
from kivy.clock import Clock, mainthread


class FlasherFlow(Screen):
    progress = 0
    bg_thread = None
    running = True
    flash_flow_locked = False
    flash_flow_start = False

    # General
    pcb_size = None
    
    temperature_option = None
    extra_time = None
    venting = None
    previous_profile = None
    error = False
    toggle = False

    pcb_next_button_text = StringProperty("Fire!")
    temp_text = StringProperty()
    extime_text = StringProperty()
    station_text = StringProperty()
    progress_text = StringProperty("...")

    def __init__(self, **kwargs):
        Screen.__init__(self, **kwargs)

    @mainthread
    def on_pre_enter(self):
        self.manager.parent.show_buttons()
        self.error = False
        self.flash_locked = False
        self.flash_start = False
        self.update_progress(0, "Select Temperature", error=False)

        # Disable/Enable the spinners
        self.ids["pcb_size_spinner"].text = ""
        self.ids["temperature_spinner"].text = ""
        self.ids["extra_time_spinner"].text = ""
        self.ids["venting_spinner"].text = ""
        self.ids["previous_profile_spinner"].text = ""
        self.ids["pcb_size_spinner"].dIsabled = True
        self.ids["temperature_spinner"].dIsabled = True
        self.ids["extra_time_spinner"].dIsabled = True
        self.ids["venting_spinner"].dIsabled = True
        self.ids["previous_profile_spinner"].dIsabled = True
        self.ids["pcb_next_button"].dIsabled = True

        # Reset Image
        self.ids["pcb_image"].source = "templates/img/pcb.png"

        self.PCBs = []
        self.TEMPs = []
        self.TIMEs = []
        self.pcb_size = ""
        self.tempature = ""
        self.extra_time = ""

    @mainthread
    def on_enter(self):
        self.running = True
        self.done_running_tests = True
        self.bg_thread = Thread(target=self.flasher_flow_thread, daemon=True)
        self.bg_thread.start()

    @mainthread
    def on_pre_leave(self):
        self.running = False
        self.flash_flow_locked = False
        self.flash_flow_start = False
        try:
          if self.bg_thread is not None:
                try:
                    self.running = False
                    self.bg_thread.join(2)
                    if self.bg_thread.is_alive():
                        self.bg_thread.kill()
                except Exception as e:
                    self.manager.parent.log(e)
                    self.manager.parent.timer_stop()
                    
    def flasher_flow_thread(self):
        time.sleep(1)
        self.populate_pcb_size_spinner()
        not_flashing_flow_now = True

        while self.running:
            time.sleep(0.1)
            if self.flash_flow_start:
                not_flashing_flow_now = False
                self.manager.parent.timer_start()
                self.do_flash_flow()
                self.manager.parent.timer_stop()
                self.flash_flow_start = False
                self.ids["pcb_next_button"].dIsabled = False
            elif self.flash_flow_locked and (self.pcb_size == "Large" or self.Times_option == "None"):
                try:
                    p = flasher_flow()
                    p.check_oven_is_ready
                    if p.check_main_connected():
                        if not_flashing_flow_now:
                            not_flashing_flow_now = False
                            self.error = False
                            self.update_progress(0, "Flash_flow...")
                            self.flash_flow_start = True
                            self.ids["pcb_next_button"].dIsabled = True
                        time.sleep(1)
                    else:
                        not_flashing_flow_now = True
                except:
                    pass
            else:
                not_flashing_flow_now = True

    @mainthread
    def reset(self):
        self.on_pre_leave()
        self.on_leave()
        self.on_pre_enter()
        self.on_enter()

    @mainthread
    def populate_pcb_size_spinner(self):
        self.ids["pcb_size_spinner"].option_cls = SpinnerOptions
        self.ids["pcb_size_spinner"].values = [
            "Large",
            "Medium",
            "Small",
            "Tiny"
        ]
        self.ids["pcb_size_spinner"].bind(text=self.populate_part_sub_class_spinner)

        # disable/enable the spinners
        self.ids["pcb_size_spinner"].text = ""
        self.ids["temperature_spinner"].text = ""
        self.ids["extra_time_spinner"].text = ""
        self.ids["venting_spinner"].text = ""
        self.ids["previous_profile_spinner"].text = ""
        self.ids["pcb_size_spinner"].dIsabled = True
        self.ids["temperature_spinner"].dIsabled = True
        self.ids["extra_time_spinner"].dIsabled = True
        self.ids["venting_spinner"].dIsabled = True
        self.ids["previous_profile_spinner"].dIsabled = True
        self.ids["pcb_next_button"].dIsabled = True

        # Reset Image
        self.ids["board_image"].source = "templates/img/pcb.png"


    @mainthread
    def populate_temperature_spinner(self, spinner, text):
        self.ids["temperature_spinner"].text = ""
        self.ids["extra_time_spinner"].text = ""
        self.ids["venting_spinner"].text = ""
        self.ids["previous_profile_spinner"].text = ""

        self.ids["temperature_spinner"].option_cls = SpinnerOptions
        if self.part_class == "Large":
           self.ids["temperature_spinner"].bind(text=self.populate_pcb_spinners)

        # dIsable/enable the spinners
        self.ids["pcb_size_spinner"].dIsabled = False
        self.ids["part_sub_class_spinner"].dIsabled = False
        self.ids["temperature_spinner"].dIsabled = False
        self.ids["extra_time_spinner"].dIsabled = True
        self.ids["venting_spinner"].dIsabled = True
        self.ids["previous_profile_spinner"].dIsabled = True
        self.ids["pcb_next_button"].dIsabled = True

        # Set Image
        self.ids["board_image"].source = "templates/img/{}.png".format(self.part_sub_class)

    @mainthread
    def populate_pcb_spinners(self, spinner, text):
        self.temperature_option = text

        self.ids["extra_time_spinner"].option_cls = BigSpinnerOptions
        self.ids["venting_spinner"].option_cls = BigSpinnerOptions
        self.ids["previous_profile_spinner"].option_cls = BigSpinnerOptions

        self.ids["extra_time_spinner"].text = ""
        self.ids["venting_spinner"].text = ""
        self.ids["previous_profile_spinner"].text = ""

        self.ids["pcb_size_spinner"].dIsabled = False
        self.ids["pcb_next_button"].dIsabled = True

        self.PCBs = []
        self.TEMPs = []
        self.TIMEs = []
        self.pcb_size = ""
        self.tempature = ""
        self.extra_time = ""

        if self.pcb_size == "Large":

            self.ids["extra_time_spinner"].bind(text=self.allow_flash_flow)
            self.ids["venting_spinner"].bind(text=self.allow_flash_flow)
            self.ids["previous_profile_spinner"].bind(text=self.allow_flash_flow)

    @mainthread
    def allow_flash_flow(self, spinner, text):
        self.extra_time = self.ids["extra_time_spinner"].text
        self. venting = self.ids["venting_spinner"].text
        self.previous_profile = self.ids["previous_profile_spinner"].text

      # if self.pcb_size == "Large":
    @mainthread
    def next_pcb(self, set_lock=False):
        if set_lock:
            self.flash_flow_locked = True

        if not self.flash_flow_locked:
            # Prompt for confirmation with a popup
            flash_flow_prompt = Popup(size_hint=(0.5, 0.5), title="start the flow?")

            bno = Button(text="Cancel", font_size="36sp")
            bno.bind(on_press=flash_flow_prompt.dismiss)
            bye = Button(text="Flow", font_size="36sp")
            bye.bind(on_press=flash_flow_prompt.dismiss)
            bye.bind(on_press=lambda x: self.next_pcb(True))

            bl2 = BoxLayout(spacing=10, size_hint=(1, 0.35))
            bl2.add_widget(bno)
            bl2.add_widget(bye)

            lab_text = """Are you sure you want to flash_flow the following?

Main: {}""".format(self.extra_time)
            if self. venting and self. venting != "":
                lab_text += "\nKeypad: {}".format(self. venting)
            if self.previous_profile and self.previous_profile != "":
                lab_text += "\nHOT: {}".format(self.previous_profile)
            lab = Label(text=lab_text, font_size="32sp")

            bl1 = BoxLayout(orientation='vertical', size_hint=(1, 1))
            bl1.add_widget(lab)
            bl1.add_widget(bl2)

            flash_flow_prompt.add_widget(bl1)
            flash_flow_prompt.open()
        else:
            self.error = False
            self.update_progress(0, "Flashing...")
            self.ids["pcb_size_spinner"].dIsabled = True
            self.ids["temperature_spinner"].dIsabled = True
            self.ids["extra_time_spinner"].dIsabled = True
            self.ids["venting_spinner"].dIsabled = True
            self.ids["previous_profile_spinner"].dIsabled = True
            self.ids["pcb_next_button"].dIsabled = True
            self.flash_start = True

    def do_flash(self):
        if self.part_class == "Large" or self.temperature_option == "HOT Module":
            if self.part_class == "Large":
                if self.extra_time != "":
                    self.extra_time = [j for j in self.MAINs if j.endswith(self.extra_time)][0]
                    self.manager.parent.log(self.extra_time, 2)
                if self. venting != "":
                    self. venting = [j for j in self.KEYPADs if j.endswith(self. venting)][0]
                    self.manager.parent.log(self. venting, 2)
                if self.previous_profile != "":
                    self.previous_profile = [j for j in self.HOTs if j.endswith(self.previous_profile)][0]
                    self.manager.parent.log(self.previous_profile, 2)
                f = PCBflasherflow(
                    self.extra_time,
                    self. venting,
                    self.previous_profile,
                )
            else:
                self.previous_profile = [j for j in self.HOTs if j.endswith(self.previous_profile)][0]
                self.manager.parent.log(self.previous_profile, 2)
                f = PCBflasherflow(
                    None,
                    None,
                    self.previous_profile,
                )
            f.LOGGER = self.manager.parent.log

            while f.progress < 100 and not f.error and self.running:
                self.update_progress(f.progress, f.status)
                time.sleep(0.1)


            # Done
            self.update_progress(100, "Flash_flow Complete")
            return True


    @mainthread
    def flash_flow_progress(self, dt):
        fg = self.ids["progress_fg"]

        if self.progress != 100:
            return

        with fg.canvas.before:
            fg.canvas.before.clear()
            if self.toggle:
                Color(0, 1, 0, 0.75)
                self.manager.parent.beep()
            else:
                Color(0, 1, 0, 0.25)
            self.toggle = not self.toggle
            Rectangle(size=(fg.size[0], fg.size[1]), pos=fg.pos)

    @mainthread
    def update_progress(self, progress, text="", error=None):
        if not progress or progress < 0 or progress > 100:
            progress = 0

        # Check for a change
        change = False

        if progress != self.progress:
            self.progress = progress
            change = True

        fg = self.ids["progress_fg"]

        if text and text != "" and text != self.progress_text:
            text = str(text)
            self.progress_text = text
            change = True

        if error is not None and error != self.error:
            self.manager.parent.log(self.progress_text)
            self.error = error
            change = True
            if error is True:
                self.manager.parent.timer_stop()

        if not change:
            return

        if not self.error:
            self.manager.parent.log(self.progress_text, level=1)

        with fg.canvas.before:
            fg.canvas.before.clear()
            if self.error:
                Color(1, 0, 0, 0.75)
            else:
                if self.progress == 100:
                    Color(0, 1, 0, 0.5)
                else:
                    Color(1, 1, 0, 0.5)
            Rectangle(size=(fg.size[0] * progress / 100, fg.size[1]), pos=fg.pos)

        if self.progress == 100:
            self.flashing_progress_thread = None
            Clock.schedule_once(self.flash_progress, 0.0)
            Clock.schedule_once(self.flash_progress, 0.5)
            Clock.schedule_once(self.flash_progress, 1.0)
            Clock.schedule_once(self.flash_progress, 1.5)
            Clock.schedule_once(self.flash_progress, 2.0)
            Clock.schedule_once(self.flash_progress, 2.5)
            self.manager.parent.timer_stop()
            self.bbb_retries = 0


class SpinnerOptions(SpinnerOption):
    def __init__(self, **kwargs):
        super(SpinnerOptions, self).__init__(**kwargs)
        self.resize((420, 50))

    @mainthread
    def resize(self, size):
        self.size = size
        self.font_size = 42
        padding = (10, 10)
        self.text_size = self.size
        self.halign = 'left'


class BigSpinnerOptions(SpinnerOptions):
    def __init__(self, **kwargs):
        super(BigSpinnerOptions, self).__init__(**kwargs)
        self.resize((960, 50))