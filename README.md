# Control Yeelight with Wacom Tablet

This is a small home project I am working on to control my Yeelight light bulb 
using a Wacom tablet. The basic idea is to use click and drag events on the 
tablet (Wacom Intuos Draw) to switch the light on and off, to change 
brightness, color temperature and color. In addition, by starting the 
light-bulb in different quadrants of the tablet (or with different clicks), I 
want to enable the bulb in different modes (e.g. color mode, reading mode, 
change with the day mode, etc...).

## The Setup

1. Yeelight lightbulb, with LAN mode enabled.

2. Raspberry Pi connected to the tablet in headless mode (running disconnected 
   from a screen).

3. PyQt5 - A QT application that runs in full-screen and continuously reads the 
   click and move events from the tablet.

4. `python-yeelight` - A python library to control the light bulb.

## Control of the light bulb

There is a very nice and simple library for python (`python-yeelight`) that 
enables the discovery and control of light bulbs. Currently it discovers all 
light bulbs and, by default, enables the first one (I only have one atm). 

## Connection to the Wacom Tablet

I'm using PyQt5 in order to receive events from the Wacom Tablet. QT5 has an 
`QTabletEvent` class that allows to specifically track tablet events. I create 
a window that covers the entire screen ([following this post][1]) and thus is 
able to get events from the entire tablet surface area. Since I intend to run 
this on a headless raspberry pi, this should not be a problem.

[1]: 
https://stackoverflow.com/questions/48873483/python-example-for-wacom-tablets

## Challenges / Problems / Limitations

1. The light bulb has a limited rate in which it can receive events. There is a 
   `music mode` which, however, doesn't seem to work. This means that after 
   using the pen to adjust brightness, the library starts yielding exceptions 
   and the connection to the bulb seems interrupted.

## Ideas

- By pressing the button on the pen, the tablet's surface would be transformed 
  to a 2D representation of the HSV color-space. Thus pressing anywhere on the 
  tablet will determine the color (as opposed to dragging to determine the 
  color, as I previously planned).

## TODO

- [ ] Debug rate limit on bulb - either find a workaround or create a smart way 
  to rate-limit the requests to the light bulb without reducing its haptic 
  response abilities.

- [ ] Design the different modes in which the light bulb will be changed. The 
  Tablet supports detecting movement in 2D, as well as pressure of the pen and 
  the pen (and tablet) has buttons to press while dragging. 

- [ ] Manage to run everything on the raspberry pi (`python-yeelight`, `QT5`, 
  the Wacom tablet itself).

- [ ] Setup the program to automatically run on startup of the pi, as well as 
  recover from crashes without intervention. 

