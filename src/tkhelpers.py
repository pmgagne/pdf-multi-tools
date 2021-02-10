import tkinter as tk
import tkinter.ttk as ttk

def widget_recursive_enabler(widget: tk.Widget, enable: bool):
    '''Enable/Disable a TK widget and all its children.''' 
    # TODO: Detect if tkwidget or ttk 
    if enable:
        state = ['!disabled']
    else:
        state = ['disabled']

    for child in widget.winfo_children():
        widget_recursive_enabler(child, enable=enable)
    
    widget.state(state)


class BusyManager:
    '''Display a busy cursor on all visible widgets
       ref http://effbot.org/zone/tkinter-busy.htm'''

    def __init__(self, widget):
        self.toplevel = widget.winfo_toplevel()
        self.widgets = {}

    def busy(self, widget=None):

        # attach busy cursor to toplevel, plus all windows
        # that define their own cursor.

        if widget is None:
            w = self.toplevel # myself
        else:
            w = widget

        if not str(w) in self.widgets:
            try:
                # attach cursor to this widget
                cursor = w.cget("cursor")
                if cursor != "watch":
                    self.widgets[str(w)] = (w, cursor)
                    w.config(cursor="watch")
            except TclError:
                pass

        for w in w.children.values():
            self.busy(w)

    def notbusy(self):
        # restore cursors
        for w, cursor in self.widgets.values():
            try:
                w.config(cursor=cursor)
            except TclError:
                pass
        self.widgets = {}