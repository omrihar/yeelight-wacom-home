import math
import os
import sys
import time

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

import yeelight

import schedule

class TabletSampleWindow(QWidget):
    def __init__(self, parent=None):
        super(TabletSampleWindow, self).__init__(parent)
        self.MAX_CLICK = 10.
        self.MOVE_CHUNK = 40
        self.BRIGHT_INC = 5
        self.CT_INC = 250
        self.MAX_PRESSURE = 50
        self.text = ""
        self.pen_pressure = 0
        self.max_pressure = 0
        self.mode = None
        self.moved = False

        # Resizing the sample window to full desktop size:
        frame_rect = app.desktop().frameGeometry()
        width, height = frame_rect.width(), frame_rect.height()
        self.resize(width, height)
        self.move(-9, 0)
        self.setWindowTitle("Yeelight Control Center")
        self.width = width
        self.height = height

        # discover all light bulbs and setup first one
        bulbs = yeelight.discover_bulbs()
        if len(bulbs) == 0:
            print("No Yeelight Bulbs discovered! exiting...")
            sys.exit(0)
        self.bulb = yeelight.Bulb(ip=bulbs[0]['ip'])
        print(f"Connected to bulb on ip {bulbs[0]['ip']}")

        self.specs = self.bulb.get_model_specs()
        self.min_ct = self.specs['color_temp']['min']
        self.max_ct = self.specs['color_temp']['max']
        self.sync_bulb()
        schedule.every(5).minutes.do(self.sync_bulb)

    def sync_bulb(self):
        if self.bulb:
            self.props = self.bulb.get_properties()
        self.on = self.props['power'] != 'off'
        self.bright = int(self.props['bright'])
        self.hue = self.props['hue']
        self.sat = self.props['sat']
        self.ct = int(self.props['ct'])

    def display(self):
        self.text = f'   mode: {self.mode}, max_pressure: {self.max_pressure} '
        self.text += f'curr_xy: ({self.curr_x}, {self.curr_y})'

    def on_press(self, tabletEvent):
        self.start_x = tabletEvent.globalX()
        self.start_y = tabletEvent.globalY()
        self.max_pressure = 0

    def on_move(self, tabletEvent):
        self.max_pressure = max(self.max_pressure, self.pen_pressure)

        if self.on and self.delta() > self.MOVE_CHUNK:
            self.moved = True
            self.on_chunk()
            self.start_x = self.curr_x
            self.start_y = self.curr_y

    def on_chunk(self):
        dx = self.curr_x - self.start_x
        dy = self.curr_y - self.start_y
        if abs(dx) > abs(dy):
            # Adjust brightness
            if dx > 0:
                if self.bright < 100:
                    self.bright += self.BRIGHT_INC
                    self.bright = min(self.bright, 100)
            else:
                if self.bright > 1:
                    self.bright -= self.BRIGHT_INC
                    self.bright = max(1, self.bright)
            try:
                self.bulb.set_brightness(self.bright)
            except yeelight.main.BulbException:
                pass
        else:
            # Adjust color temperature
            if dy > 0:
                if self.ct < self.max_ct:
                    self.ct += self.CT_INC
                    self.ct = min(self.ct, self.max_ct)
            else:
                if self.ct > self.min_ct:
                    self.ct -= self.CT_INC
                    self.ct = max(self.min_ct, self.ct)
            try:
                self.bulb.set_color_temp(self.ct)
            except yeelight.main.BulbException:
                pass

    def on_release(self, tabletEvent):
        if self.on and self.delta() < self.MAX_CLICK and not self.moved:
            if self.max_pressure > self.MAX_PRESSURE:
                self.click()
            else:
                self.set_position_color()
        elif not self.on:
            self.click()

        self.moved = False

    def set_position_color(self):
        hue = math.floor((self.curr_x / self.width) * 360) % 359
        sat = 100 - math.floor((self.curr_y / self.height) * 100)
        try:
            self.bulb.set_hsv(hue=hue, saturation=sat)
        except yeelight.main.BulbException:
            pass
            # pyqtRemoveInputHook()
            # import subprocess; subprocess.call(['notify-send', 'Excuse me...']);
            # import IPython; IPython.embed()
        self.hue = hue
        self.sat = sat

    def init_bulb(self):
        if self.mode == 0:
            self.bulb.set_brightness(30)
            self.bulb.set_hsv(hue=187, saturation=57, value=30)
            self.bulb.set_color_temp(3500)
        elif self.mode == 1:
            pass
        elif self.mode == 2:
            pass
        elif self.mode == 3:
            pass

    def click(self):
        try:
            self.bulb.toggle()
            self.on = not self.on
            if self.on:
                if self.start_x < self.width / 2:
                    if self.start_y < self.height / 2:
                        self.mode = 0
                    else:
                        self.mode = 2
                else:
                    if self.start_y < self.height / 2:
                        self.mode = 1
                    else:
                        self.mode = 3
                self.init_bulb()
        except yeelight.main.BulbException:
            pass

    def delta(self):
        return math.sqrt((self.curr_x - self.start_x)**2 + (self.curr_y -
                                                           self.start_y)**2)

    def tabletEvent(self, tabletEvent):
        self.curr_x = tabletEvent.globalX()
        self.curr_y = tabletEvent.globalY()
        self.pen_pressure = int(tabletEvent.pressure() * 100)

        if tabletEvent.type() == QTabletEvent.TabletPress:
            self.on_press(tabletEvent)
        elif tabletEvent.type() == QTabletEvent.TabletMove:
            self.on_move(tabletEvent)
        elif tabletEvent.type() == QTabletEvent.TabletRelease:
            self.on_release(tabletEvent)

        self.display()
        tabletEvent.accept()
        self.update()

    def paintEvent(self, event):
        text = self.text
        i = text.find("\n\n")
        if i >= 0:
            text = text.left(i)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.TextAntialiasing)
        painter.drawText(self.rect(), Qt.AlignTop | Qt.AlignLeft , text)

app = QApplication(sys.argv)
mainform = TabletSampleWindow()
mainform.show()
app.exec_()
