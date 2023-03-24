import time, sys, io, serial, json, requests
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.stacklayout import StackLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.anchorlayout import AnchorLayout
from kivy.graphics import Canvas, Color, Rectangle, InstructionGroup
from kivy.core.window import Window
from kivy.clock import mainthread
from threading import Thread


class MainFlow(Screen):
    def __init__(self, **kwargs):
        self.RUNNING = True
        self.REFRESH = True
        self.REFRESH_INTERVAL = True
        self.bg_refresh = None
        Screen.__init__(self, **kwargs)
        Window.bind(on_request_close=self.stop_refresh)

    def on_pre_enter(self):
        self.manager.parent.show_buttons(main_flow=True)

    def on_enter(self):
        self.manager.parent.ids["settings"].load_settings()
        self.manager.parent.change_name(self.manager.current)
        self.RUNNING = True
        self.bg_refresh = Thread(target=self.refresh_loop, daemon=True)
        self.bg_refresh.start()

    def on_pre_leave(self, *args, **kwargs):
        self.RUNNING = False
        if self.bg_refresh is not None:
            try:
                self.bg_refresh.join(1)
            except:
                pass

    def refresh_loop(self):
        # Idle Timeout
        self.timeout_timer = time.time()
        while self.RUNNING:
            if abs(time.time() - self.timeout_timer) > self.manager.timeout_time and not self.manager.no_login_station:
                self.RUNNING = False
                self.manager.parent.error_popup("bummer")
                self.manager.parent.back(True)
                return
            for i in range(self.REFRESH_INTERVAL * 10):
                if not self.RUNNING:
                    return
                if self.REFRESH:
                    self.REFRESH = False
                break
            time.sleep(0.1)


class job(BoxLayout):
    def __init__(self, manager, **kwargs):
        self.manager = manager
        BoxLayout.__init__(self, **kwargs)
        self.size_hint = (1, 0.2)
        self.padding = (10, 10)
        self.set_bg_color(0.15, 0.15, 0.15, 0.9)
        self.orientation = 'horizontal'
        self.test_station = False

    def fill(self, job):
        if not job or job is [] or job is "":
            return False

        self.clear_widgets()

        self.job = job
        self.test_station = self.manager.test_station

        col_l = StackLayout(size_hint=(0.45, 1), orientation='tb-lr')
        col_m = StackLayout(size_hint=(0.10, 1), orientation='tb-lr')
        col_r = StackLayout(size_hint=(0.45, 1), orientation='tb-lr')



        # Pcb size
        lab_pn = Label(halign='left', valign='middle', size_hint=(1, 0.2), markup=True, font_size=20)
        lab_pn.bind(size=lab_pn.setter('text_size'))
        lab_pn.text = "[b]Pcb_size:[/b] " + job["Pcb_size"]
        col_l.add_widget(lab_pn)


        # job Date
        lab_od = Label(halign='right', valign='middle', size_hint=(1, 0.2), markup=True, font_size=20)
        lab_od.bind(size=lab_od.setter('text_size'))
        lab_od.text = "[b]job Date:[/b] " + job["jobDate"]
        col_r.add_widget(lab_od)

        # job Progress
        lab_qt = Label(halign='right', valign='middle', size_hint=(1, 0.2), markup=True, font_size=20)
        lab_qt.bind(size=lab_qt.setter('text_size'))
        lab_qt.text = "[b]Progress:[/b] "
        col_r.add_widget(lab_qt)

        # Flow Button
        build_button = Button(text="Fire Pcb >", size_hint=(0.4, 0.75), font_size=24)
        build_button.bind(on_release=lambda x: self.build_job())
        build_button_wrapper = AnchorLayout(anchor_x="right", anchor_y="bottom", size_hint=(1, 0.6))
        build_button_wrapper.add_widget(build_button)
        col_r.add_widget(build_button_wrapper)

        self.add_widget(col_l)
        self.add_widget(col_m)
        self.add_widget(col_r)

    def set_bg_color(self, r, g, b, a):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(r, g, b, a)
            self.rect = Rectangle(pos=self.pos, size=self.size)

        self.bind(pos=self.update_rect, size=self.update_rect)

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

    def build_job(self, job):
        if job is None or job == "":
            return False

        self.manager.current_job = job
        self.manager.transition.direction = 'left'
        self.manager.current = "pcb_flow"