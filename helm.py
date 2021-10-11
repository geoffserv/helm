# helm
#
# Proof of concept MIDI instrument

# using pygame as the canvas https://www.pygame.org/docs/

import pygame
from pygame.locals import *

import helm_fonts
from helm_controls import WheelControl, ChordControl
import helm_globals

if helm_globals.using_griffin_powermate:
    from dqpypowermate import Powermate


class Helm:
    def __init__(self, canvas_width=1920, canvas_height=1080, init_gfx=True):

        self.powermate = None
        if helm_globals.using_griffin_powermate:
            powermate_path = "/dev/input/by-id/usb"
            powermate_path += "-"
            powermate_path += "Griffin_Technology__Inc."
            powermate_path += "_"
            powermate_path += "Griffin_PowerMate"
            powermate_path += "-"
            powermate_path += "event-if00"
            self.powermate = Powermate(powermate_path)

        # Graphics attributes
        # Clock, for tracking events and frame rate
        self.clock = pygame.time.Clock()

        self.fullscreen = False

        self.canvas_width = canvas_width
        self.canvas_height = canvas_height

        self.r = int(
            (canvas_height * .8) / 2)  # R is half of __% of the screen

        self.running = False  # will be True once self.run() is called

        # Initialize the canvas
        pygame.init()

        # Initialize the fonts
        helm_fonts.init_fonts()

        if init_gfx:
            # If this is being run headless, turn initGfx to False
            # This is useful for headless CI testing
            if self.fullscreen:
                self.canvas = pygame.display.set_mode(
                    [self.canvas_width, self.canvas_height], pygame.NOFRAME)
                pygame.display.toggle_fullscreen()
                # Workaround for pygame.FULLSCREEN going blank in Ubuntu
            else:
                self.canvas = pygame.display.set_mode(
                    [self.canvas_width, self.canvas_height])
            pygame.display.set_caption('helm')  # Set the window title for fun

        # controlSurfaces list contains each controlSystem object that is
        # rendered.
        # Declare controlSystem objects, set them up and init them,
        # then append() them
        # to this list.  Then each in turn will get a drawControl() call and
        # their
        # surface attribute will be blit to the canvas.
        self.controlSurfaces = []

        # ffWheel (fourth/fifth wheel) handles keystrokes related to key,
        #   mode root, and note selection around a circle of fifths.

        # The size of the ffWheel's surface will be __% of the screen
        control_ff_wheel_size = int(self.canvas_height * 0.98)
        # Create a ffWheel control.  Init.
        control_ff_wheel = WheelControl(canvas_size=control_ff_wheel_size)

        # control_chord handles keystrokes related to which chord notes
        #   to trigger, such a major triad/etc.  It takes a wheelControl
        #   argument to link up with the ffWheel and pass chord info

        # Append the ffWheel to the controlSurfaces list
        self.controlSurfaces.append(control_ff_wheel)

        # The size of the control_chord surface will be __% of the screen
        control_chord_size = int(self.canvas_width * 0.40)
        # Create a chord control.  Init.
        control_chord = ChordControl(canvas_size=control_chord_size,
                                     blit_x=int(self.canvas_width / 2) + 130 +
                                     helm_globals.canvas_margin,
                                     blit_y=helm_globals.canvas_margin + 30)

        # Append the chord control to the controlSurfaces list
        self.controlSurfaces.append(control_chord)

    def run(self):
        self.running = True

        self.canvas.fill(helm_globals.color_black)

        # The main running loop
        while self.running:

            # First, draw the screen:
            # Loop through each controlSystem added to the controlSurfaces list
            for controlSurface in self.controlSurfaces:
                # The drawControl method should update the control's visual
                # elements and
                # draw to the control's surface
                controlSurface.draw_control()
                # Blit the control's surface to the canvas
                self.canvas.blit(controlSurface.surface,
                                 [controlSurface.blit_x,
                                  controlSurface.blit_y])
            pygame.display.update()

            # Next, Update controls and everything in preparation for the
            # next loop through:
            events = {}  # Record events seen during this execution here.
            # Key is a label, usually pygame event
            # The controlSurfaces themselves should know what to look for
            # and what to do.
            for event in pygame.event.get():
                if event.type == QUIT:  # If the window 'close' button...
                    self.running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
                    if event.key == pygame.K_COMMA:
                        events["key_clockwise"] = True
                    if event.key == pygame.K_PERIOD:
                        events["key_counterclockwise"] = True
                    if event.key == pygame.K_q:
                        events["chord_clockwise"] = True
                    if event.key == pygame.K_e:
                        events["chord_counterclockwise"] = True
                    if event.key == pygame.K_a:
                        events["chord_majortriad_start"] = True
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_a:
                        events["chord_majortriad_stop"] = True

            if helm_globals.using_griffin_powermate:
                event = self.powermate.read_event(timeout=0)
                if event:
                    if event[2] == 1:
                        events["K_a"] = True
                    if event[2] == -1:
                        events["K_d"] = True

            for controlSurface in self.controlSurfaces:
                controlSurface.update_control(
                    events)  # update control attributes with a dict of events

            self.clock.tick(60)  # 60 fps

        # If we've reached this point, we've escaped the run: loop.  Quit.
        pygame.quit()


if __name__ == "__main__":
    helm = Helm()
    helm.run()
