import tkinter as tk
import tkinter.ttk as ttk

def widget_recursive_enabler(widget: tk.Widget, enable: bool):
 
    # TODO: Detect if tkwidget or ttk 
    if enable:
        state = ['!disabled']
    else:
        state = ['disabled']

    for child in widget.winfo_children():
        widget_recursive_enabler(child, enable=enable)
    
    widget.state(state)