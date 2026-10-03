from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner
from kivy.core.text import LabelBase
from datetime import datetime, timedelta
import db


LabelBase.register(name="Poppins", fn_regular="Fonts/Poppins-Regular.ttf")
LabelBase.register(name="Treb", fn_regular="Fonts/Trebuchet.ttf")
# Recipient Login Screen
class RecipientLoginScreen(Screen):
    def login(self):
        email = self.ids.email_input.text.strip()
        recipient = db.get_recipient_by_email(email)
        if recipient:
            screen_name = f"recipient_{email}"
            if not self.manager.has_screen(screen_name):
                self.manager.add_widget(RecipientScreen(name=screen_name, recipient_email=email))
            self.manager.current = screen_name
        else:
            self.ids.message.text = " Ask Your Provider to Set Up the Account"
#Testing Purposes
    def switch_to_provider(self):
        self.manager.current = "provider_screen"

# Recipient Screen
class RecipientScreen(Screen):
    def __init__(self, recipient_email, **kwargs):
        super().__init__(**kwargs)              #Can't enter email without this
        self.recipient_email = recipient_email
        self.recipient = db.get_recipient_by_email(recipient_email)
        self.reminder_event = None
        Clock.schedule_once(lambda dt: self.update_last_checkin(), 0)
        Clock.schedule_once(lambda dt: self.start_reminder(), 0)

    def check_in(self):
        ts = db.save_checkin(self.recipient[0])
        self.ids.status_label.text = f" Checked in at {ts}"
        self.ids.last_checkin.text = f"Last check-in: {ts}"
        self.start_reminder()
        # Simulated notification
        print(f"[NOTIFICATION] {self.recipient[1]} ({self.recipient[2]}) checked in at {ts}")

    def update_last_checkin(self):
        last = db.get_last_checkin(self.recipient[0])
        self.ids.last_checkin.text = f"Last check-in: {last if last else 'N/A'}"

    def start_reminder(self):
        self.cancel_reminder()
        interval_hours = self.recipient[3] if self.recipient and len(self.recipient) > 3 else 2
        interval_seconds = interval_hours * 60
        self.reminder_event = Clock.schedule_once(self.show_reminder, interval_seconds)

    def show_reminder(self, dt):
        last_check = db.get_last_checkin(self.recipient[0])
        self.ids.status_label.text = " Reminder: Are you OK?"
        if last_check:
            last_time = datetime.strptime(last_check, "%Y-%m-%d %H:%M:%S")
            interval_hours = self.recipient[3] if len(self.recipient) > 3 else 2
            if datetime.now() - last_time > timedelta(hours=interval_hours):
                db.add_alert(self.recipient[0], "Missed check-in!")
        self.start_reminder()

    def cancel_reminder(self):
        if self.reminder_event:
            self.reminder_event.cancel()
            self.reminder_event = None

    def switch_to_provider(self):
        self.manager.current = "provider_screen"

# Provider Screen
class ProviderScreen(Screen):
    def on_pre_enter(self):
        Clock.schedule_once(lambda dt: self.refresh_recipients())
        Clock.schedule_once(lambda dt: self.refresh_alerts())
        self.refresh_dropdown()

    def add_recipient(self):
        name = self.ids.new_name.text.strip()
        email = self.ids.new_email.text.strip()
        interval = self.ids.new_interval.text.strip()
        if name and email and interval.isdigit():
            db.add_recipient(name,email,int(interval))
            self.ids.new_name.text = ""
            self.ids.new_email.text = ""
            self.ids.new_interval.text = ""
            self.refresh_recipients()
            self.refresh_dropdown()

    def delete_recipient(self, email):
        db.delete_recipient(email)
        screen_name = f"recipient_{email}"
        if self.manager.has_screen(screen_name):
            self.manager.remove_widget(self.manager.get_screen(screen_name))
        self.refresh_recipients()
        self.refresh_dropdown()

    def refresh_recipients(self):
        self.ids.recipients_list.clear_widgets()
        recipients = db.get_recipients()
        for r in recipients:
            last_check = db.get_last_checkin(r[0])
            interval_hours = r[3] if len(r) > 3 and r[3] else 2
            row = BoxLayout(orientation="horizontal", size_hint_y=None, height=40, spacing=10)
            row.add_widget(Label(text=f"{r[1]} ({r[2]}) — Interval: {interval_hours}h — Last: {last_check if last_check else 'N/A'}", font_size=16))
            btn = Button(text="Delete", size_hint_x=0.2, on_press=lambda inst, email=r[2]: self.delete_recipient(email))
            row.add_widget(btn)
            self.ids.recipients_list.add_widget(row)

    def refresh_alerts(self):
        self.ids.alerts_list.clear_widgets()
        alerts = db.get_alerts()
        for a in alerts:
            text = f"{a[1]} — {a[2]} — {a[3]}"
            self.ids.alerts_list.add_widget(Label(text=text, font_size=16))

    def refresh_dropdown(self):
        self.ids.recipient_dropdown.values = [r[2] for r in db.get_recipients()]

    def switch_to_login(self):
        self.manager.current = "login_screen"

    def switch_to_recipient(self):
        email = self.ids.recipient_dropdown.text
        if email and email != "Select Recipient":
            screen_name = f"recipient_{email}"
            if not self.manager.has_screen(screen_name):
                self.manager.add_widget(RecipientScreen(name=screen_name, recipient_email=email))
            self.manager.current = screen_name

# Screen Manager 
class CareScreenManager(ScreenManager):
    pass

# KV 
kv = """
<RecipientLoginScreen>:
    canvas.before:
        Color:
            rgba: 0, 0.137, 0.4, 0.7
        Rectangle:
            pos: self.pos
            size: self.size
    BoxLayout:
        orientation: "vertical"
        padding: 20
        spacing: 20

        Label:
            text: "Recipient Login"
            font_name: "Poppins"
            font_size: 40

        TextInput:
            id: email_input
            hint_text: "Enter your email"
            font_name: "Treb"
            size_hint_y: 0.25
            font_size: 24

        Label:
            id: message
            text: ""
            font_name: "Poppins"
            font_size: 24
            color: 1,0,0,1

        Button:
            background_normal: ""
            background_color: 0.498, 0.624, 1.0, 1
            text: "Login"
            font_name: "Poppins"
            size_hint_y: 0.2
            font_size: 28
            on_press: root.login()

        Button:
            background_normal: ""
            background_color: 0.498, 0.624, 1.0, 1
            text: "Switch to Provider Screen"
            font_name: "Poppins"
            size_hint_y: 0.2
            font_size: 28
            on_press: root.switch_to_provider()

<RecipientScreen>:
    canvas.before:
        Color:
            rgba: 0, 0.137, 0.4, 0.7
        Rectangle:
            pos: self.pos
            size: self.size
    BoxLayout:
        orientation: "vertical"
        padding: 20
        spacing: 20

        Label:
            id: status_label
            text: "Press 'I'm OK' when you're okay"
            font_name: "Poppins"
            font_size: 24

        Label:
            id: last_checkin
            text: "Last check-in: N/A"
            font_name: "Poppins"
            font_size: 20

        Button:
            background_normal: ""
            background_color: 0.498, 0.624, 1.0, 1
            text: "I'm OK "
            font_name: "Poppins"
            size_hint: (1,0.2)
            font_size: 30
            on_press: root.check_in()

        Button:
            background_normal: ""
            background_color: 0.498, 0.624, 1.0, 1
            text: "Switch to Provider Screen"
            font_name: "Poppins"
            size_hint_y: 0.2
            on_press: root.switch_to_provider()
            font_size: 24

<ProviderScreen>:
    canvas.before:
        Color:
            rgba: 0, 0.137, 0.4, 0.7
        Rectangle:
            pos: self.pos
            size: self.size
    BoxLayout:
        orientation: "vertical"
        padding: 20
        spacing: 20

        Label:
            text: "Provider Dashboard"
            font_name: "Poppins"
            font_size: 24

        ScrollView:
            GridLayout:
                id: recipients_list
                cols: 1
                size_hint_y: None
                height: self.minimum_height
                row_default_height: 40
                row_force_default: True
                font_name: "Poppins"

        Label:
            text: "Missed Alerts"
            font_name: "Poppins"
            font_size: 28

        ScrollView:
            GridLayout:
                id: alerts_list
                cols: 1
                size_hint_y: None
                height: self.minimum_height
                row_default_height: 40
                row_force_default: True
                font_name: "Poppins"

        BoxLayout:
            orientation: "horizontal"
            size_hint_y: 0.4
            spacing: 50
           
            
            TextInput:
                id: new_name
                hint_text: "Recipient Name"
                font_name: "Poppins"
                font_size: 24

            TextInput:
                id: new_email
                hint_text: "Recipient Email"
                font_name: "Poppins"
                font_size: 24
                
            TextInput:
                id: new_interval
                hint_text: "Interval Hours"
                font_name: "Poppins"
                font_size: 24
                
            Button:
                background_normal: ""
                background_color: 0.498, 0.624, 1.0, 1
                text: "Add Recipient"
                font_name: "Poppins"
                on_press: root.add_recipient()
                size_hint_y: 1
                font_size: 24

        BoxLayout:
            orientation: "horizontal"
            size_hint_y: 0.4
            spacing: 70

            Button:
                background_normal: ""
                background_color: 0.498, 0.624, 1.0, 1
                text: "Switch to Recipient Login"
                font_name: "Poppins"
                on_press: root.switch_to_login()
                font_size: 24
                

            Spinner:
                background_normal: ""
                background_color: 0.498, 0.624, 1.0, 1
                id: recipient_dropdown
                text: "Select Recipient"
                font_name: "Poppins"
                values: []
                size_hint_x: 0.5
                font_size: 24
                

            Button:
                background_normal: ""
                background_color: 0.498, 0.624, 1.0, 1
                text: "Go"
                font_name: "Poppins"
                size_hint_x: 0.2
                on_press: root.switch_to_recipient()
                font_size: 24
                
"""

Builder.load_string(kv)

# App
class CareApp(App):
    def build(self):
        db.init_db()
        sm = CareScreenManager()
        sm.add_widget(RecipientLoginScreen(name="login_screen"))
        sm.add_widget(ProviderScreen(name="provider_screen"))
        sm.current = "login_screen"
        return sm

if __name__ == "__main__":
    CareApp().run()
