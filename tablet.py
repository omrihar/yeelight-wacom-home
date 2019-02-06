import math
import os
import sys
import time

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

import yeelight


class TabletSampleWindow(QWidget):
    def __init__(self, parent=None):
        super(TabletSampleWindow, self).__init__(parent)
        self.pen_x = 0
        self.pen_y = 0
        self.dir_x = 0
        self.dir_y = 0
        self.pen_pressure = 0
        self.moving = False
        self.MAX_CLICK = 10.
        self.text = ""

        # Resizing the sample window to full desktop size:
        frame_rect = app.desktop().frameGeometry()
        width, height = frame_rect.width(), frame_rect.height()
        self.resize(width, height)
        self.move(-9, 0)
        self.setWindowTitle("Yeelight Control Center")

        # discover all light bulbs and setup first one
        bulbs = yeelight.discover_bulbs()
        if len(bulbs) == 0:
            print("No Yeelight Bulbs discovered! exiting...")
            sys.exit(0)
        self.bulb = yeelight.Bulb(ip=bulbs[0]['ip'])
        print(f"Connected to bulb on ip {bulbs[0]['ip']}")

        self.props = self.bulb.get_properties()
        self.specs = self.bulb.get_model_specs()

        self.on = self.props['power'] != 'off'
        if self.on:
            self.text += 'light on'
        else:
            self.text += 'light off'

    def on_press(self, tabletEvent):
        self.start_x = tabletEvent.globalX()
        self.start_y = tabletEvent.globalY()
        self.moving = False

    def on_move(self, tabletEvent):
        self.curr_x = tabletEvent.globalX()
        self.curr_y = tabletEvent.globalY()

        self.dir_x = self.curr_x - self.start_x
        self.dir_y = self.curr_y - self.start_y

        self.moving = self.delta() > self.MAX_CLICK
        self.adjust_brightness(tabletEvent)

    def adjust_brightness(self, tabletEvent):
        if self.moving and self.on:
            self.text = "adjusting"
            try:
                if self.dir_x > 0:
                    self.bulb.set_adjust('increase', 'bright')
                else:
                    self.bulb.set_adjust('decrease', 'bright')
            except yeelight.main.BulbException as exc:
                pass

    def on_release(self, tabletEvent):
        self.curr_x = tabletEvent.globalX()
        self.curr_y = tabletEvent.globalY()

        if self.delta() < 10:
            self.click()

        self.moving = False

    def click(self):
        try:
            self.bulb.toggle()
            self.on = not self.on
        except yeelight.main.BulbException:
            # Number of event exceed 60 / second
            pass

    def delta(self):
        return math.sqrt((self.curr_x - self.start_x)**2 + (self.curr_y -
                                                           self.start_y)**2)

    def tabletEvent(self, tabletEvent):
        self.pen_x = tabletEvent.globalX()
        self.pen_y = tabletEvent.globalY()
        self.pen_pressure = int(tabletEvent.pressure() * 100)

        if tabletEvent.type() == QTabletEvent.TabletPress:
            self.on_press(tabletEvent)
        elif tabletEvent.type() == QTabletEvent.TabletMove:
            self.on_move(tabletEvent)
        elif tabletEvent.type() == QTabletEvent.TabletRelease:
            self.on_release(tabletEvent)
        self.text += " at x={0}, y={1}, pressure={2}%,".format(self.pen_x, self.pen_y, self.pen_pressure)

        if self.moving:
            self.text += ' moving'
        else:
            self.text += ' not moving'

        self.text += f' dir_x={self.dir_x} dir_y={self.dir_y}'

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
