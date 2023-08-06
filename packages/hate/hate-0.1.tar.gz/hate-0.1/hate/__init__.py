#!/usr/bin/python

"""

HATE: the High Availability Terminal Emulator.

Gnome Terminal crashes all the *god damned* time.

Xterminal doesn't work properly with 'screen' because it ignores its own 'ASCII
Del' preference setting.

Other terminals look awful on my desktop.

This is a simple replacement terminal that should do everything I need.

"""

import os
import vte
import gtk.gdk
import ConfigParser

def nop(*_args, **_kwargs):
    """ Do Nothing """

# Just guessing, from header file

VTE_ERASE_AUTO = 0
VTE_ERASE_ASCII_BACKSPACE = 1
VTE_ERASE_ASCII_DELETE = 2
VTE_ERASE_DELETE_SEQUENCE = 3

DEFAULT_FONT = 'Monospace'

def getFont():
    """
    @return: The name of the font to use, as per the configuration file.
    """
    config = getConfiguration()
    try:
        return config.get('main', 'font')
    except ConfigParser.Error:
        return DEFAULT_FONT

# global cache of the configuration
configuration = None
def getConfiguration(reload=False):
    """
    Read the configuration from the users $HOME/.hate/hate.ini or from
    $HOME/.haterc Stop at the first one that reads correctly.

    @return: ConfigParser instance with the configuration loaded.
    """
    global configuration
    if configuration and not reload:
        return configuration
    config = ConfigParser.ConfigParser()
    for filename in '~/.hate/hate.ini', '~/.haterc':
        if config.read(os.path.expanduser(filename)):
            configuration = config
            return config
    return config

def _loadIcon(iconfile):
    return gtk.gdk.pixbuf_new_from_file(
            os.path.join(os.path.expanduser('~/.hate/images'), iconfile))

icons = []
def getIcons():
    # empty the icon list before we start.
    icons[:] = []
    try:
        icon_index = file(os.path.expanduser('~/.hate/images/index.txt'))
    except IOError:
        # don't worry if we can't read the icons index file.
        return

    for line in icon_index:
        name, iconfile = line.split()
        icons.append((name, _loadIcon(iconfile)))

    return icons

class Hate(object):

    def __init__(self, container, titleFunc=nop, exitFunc=nop):
        term = self.term = vte.Terminal()
        self.exitFunc = exitFunc

        self.topwidget = tw = gtk.HBox()

        self.term.connect("window-title-changed",
                          self.titleChanged)
        self.term.connect("child-exited",
                          self.exited)

        tw.pack_start(self.term, expand=True)
        tw.pack_start(gtk.VScrollbar(self.term.get_adjustment()), expand=False)

        # set colors
        cm = self.term.get_colormap()

        fg = cm.alloc_color("white")
        bg = cm.alloc_color("black")
        cols = []

        for x in ["#000000000000",
                  "#aaaa00000000",
                  "#0000aaaa0000",
                  "#aaaa55550000",
                  "#00000000aaaa",
                  "#aaaa0000aaaa",
                  "#0000aaaaaaaa",
                  "#aaaaaaaaaaaa",
                  "#555555555555",
                  "#ffff55555555",
                  "#5555ffff5555",
                  "#ffffffff5555",
                  "#55555555ffff",
                  "#ffff5555ffff",
                  "#5555ffffffff",
                  "#ffffffffffff"]:

            cols.append(cm.alloc_color(x))

        term.set_colors(fg, bg, cols)

        # Random preferences crap:


        term.set_font_from_string(getFont())
        term.set_cursor_blinks(True)
        self.doTransparency(0.15)
        term.set_scrollback_lines(2000)
        term.set_backspace_binding(VTE_ERASE_ASCII_DELETE)
        term.set_audible_bell(True)
        term.set_visible_bell(False)

        self.reparent(container, titleFunc)

    container = None
    currentTitle = ''

    def doTransparency(self, amount):
        """
        Set the window to be the appropriate amount transparent, using
        compositing manager if available.

        @param amount: a floating point number between 0.0 (completely opaque)
        and 1.0 (completely transparent).
        """
        if self.term.get_screen().is_composited():
            self.term.set_opacity(int(0xffff * (1.0 - amount)))
        else:
            self.term.set_background_transparent(True)
            self.term.set_background_saturation(amount)


    def reparent(self, newContainer, newTitleFunc):
        if self.container is not None:
            self.container.remove(self.topwidget)
        self.container = newContainer
        self.container.add(self.topwidget)
        self.titleFunc = newTitleFunc

    def titleChanged(self, termObj):
        newTitle = termObj.get_window_title()
        self.currentTitle = newTitle
        self.titleFunc(self.currentTitle)

    def exited(self, termObj):
        self.exitFunc()

    def start(self):
        self.term.fork_command(os.environ['SHELL'])

    def geometry_hints(self):
        xpad, ypad = self.term.get_padding()
        wid = self.term.get_char_width()
        hig = self.term.get_char_height()
        return dict(base_width=xpad,
                    base_height=ypad,
                    width_inc=wid,
                    height_inc=hig,
                    min_width=xpad + wid * 4,
                    min_height = ypad + hig * 2)

ALL_WINDOWS = []

class HateWindow:
    def __init__(self):

        self.icons = getIcons()

        self.win = gtk.Window()
        self.vbox = gtk.VBox()
        self.win.add(self.vbox)
        self.hate = Hate(self.vbox, self.changeTitle, self.processEnded)
        self.win.connect("destroy", self.destroyed)

        self.ico = gtk.gdk.pixbuf_new_from_file(
            os.path.join(os.path.join(os.path.dirname(__file__)),
                         "hateicon.svg"))
        self.win.set_icon(self.ico)

        accelGroup = gtk.AccelGroup()
        self.ag = accelGroup = gtk.AccelGroup()
        self.win.add_accel_group(accelGroup)
        accelGroup.connect_group(ord('n'), (gtk.gdk.CONTROL_MASK |
                                 gtk.gdk.SHIFT_MASK), gtk.ACCEL_LOCKED,
                                 self.newterm)

        # before we show anything, initialize transparency
        screen = self.win.get_screen()
        alpha = screen.get_rgba_colormap()
        if alpha and screen.is_composited():
            self.win.set_colormap(alpha)

        self.win.show_all()
        self.hate.start()
        self.win.set_geometry_hints(self.hate.term,
                                    **self.hate.geometry_hints())

        ALL_WINDOWS.append(self)

    def newterm(self, *ev):
        HateWindow()

    def destroyed(self, ev=None):
        ALL_WINDOWS.remove(self)
        if not ALL_WINDOWS:
            gtk.main_quit()

    lastTitle = ''

    def changeTitle(self, newTitle):
        self.lastTitle = newTitle
        self.win.set_title(newTitle)
        for name, icon in icons:
            if newTitle.strip().lower().startswith(name):
                self.win.set_icon(icon)
                return
        self.win.set_icon(self.ico)

    def processEnded(self):
        self.win.set_title(self.lastTitle+" - hate <defunct>")
        self.win.destroy()
        # self.hate.start()
        # self.hate.term.feed("<<<EXITED>>>\r\n")


def main():
    HateWindow()
    gtk.main()

if __name__ == '__main__':
    main()
