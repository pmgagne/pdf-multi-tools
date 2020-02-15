#!/usr/bin/env python

import sys
import os.path

import tkinter as tk
from tkinter import ttk
import tkinter.filedialog
from tkinter.messagebox import showerror

import pdfmanipulation
import tkhelpers

class Application(ttk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.pack(expand=1, fill='both')
        self.master.title('pdf multi tool')
        
        self.last_inputfile1 = None
        self.last_inputfile2 = None
        self.last_outputfile = None

        self.input1_filename = tk.StringVar()
        self.input1_reverse = tk.IntVar()
        self.input1_reverse.set(0)

        self.input2_filename = tk.StringVar()
        self.input2_reverse = tk.IntVar()
        self.input2_reverse.set(1)

        self.output_filename = None
        self.mode = tk.IntVar()
        self.mode.set(0)

        self.create_widgets()
        self.gui_update()
        # Not resizeable.
        #ttk.Sizegrip().pack(side='right')

    def create_widgets(self):

        # Input file 1
        lf1 = ttk.LabelFrame(self, text='File 1:', padding=(12,6))
        lf1.grid(row=0, column=0, sticky=tk.EW, padx=6, pady=12)
        lf1.grid_columnconfigure(0, minsize=100, weight=1)

        filename = ttk.Entry(
            master=lf1, 
            text="Input File 1", 
            textvariable=self.input1_filename)
        filename.grid(row=0, column=0, sticky=tk.EW)
        
        filename_chooser = ttk.Button(
            master=lf1, 
            text="\N{Horizontal Ellipsis}", # aka "..."
            command=lambda:self.prompt_for_input_file(self.input1_filename) )
        filename_chooser.grid(row=0, column=1)

        input1_reverse = ttk.Checkbutton(
            master=lf1, 
            text="Reverse", 
            variable=self.input1_reverse)
        input1_reverse.grid(row=1, column=0, sticky=tk.W)

        # Input file 2
        lf2 = ttk.LabelFrame(self, text='File 2:', padding=(12,6))
        lf2.grid(row=1, column=0, sticky=tk.EW, padx=6, pady=6)
        lf2.grid_columnconfigure(0, minsize=100, weight=1)
        self.lf2 = lf2

        filename = ttk.Entry(
            master=lf2, 
            text="Input File 2", 
            textvariable=self.input2_filename)
        filename.grid(row=0, column=0, sticky=tk.EW)
        
        filename_chooser = ttk.Button(
            master=lf2, 
            text="\N{Horizontal Ellipsis}", # aka "..."
            command=lambda:self.prompt_for_input_file(self.input2_filename) )
        filename_chooser.grid(row=0, column=1)

        input2_reverse = ttk.Checkbutton(
            master=lf2, 
            text="Reverse", 
            variable=self.input2_reverse)
        input2_reverse.grid(row=1, column=0, sticky=tk.W)

        # Output file
        lf3 = ttk.LabelFrame(self, text='Output:', padding=(12,6))
        lf3.grid(row=2, column=0, sticky=tk.EW, padx=6, pady=6)
        lf3.grid_columnconfigure(0, minsize=100, weight=1)

        lf3_buttons = ttk.LabelFrame(lf3, text="Mode:", padding=(12,6))
        lf3_buttons.grid(row=1, column=0)
        
        ttk.Radiobutton(
            lf3_buttons, 
            text='Recto/Verso', 
            variable=self.mode, 
            value = 0,
            command=self.gui_update).grid(row=0,column=0)
        ttk.Radiobutton(
            lf3_buttons, 
            text='Append',
            variable=self.mode,
            value = 1,
            command=self.gui_update).grid(row=0,column=1)
        ttk.Radiobutton(
            lf3_buttons, 
            text='Prepend', 
            variable=self.mode, 
            value = 2,
            command=self.gui_update).grid(row=0,column=2)

        lf4 = ttk.Frame(self)
        lf4.grid(row=3, column=0, sticky=tk.S+tk.EW, padx=12, pady=12)
        lf4.columnconfigure(6, weight=1)
        
        self.combine_btn = ttk.Button(
            master=lf4,
            text='Process',
            command=self.process_pdf)
        self.combine_btn.grid(row=0, column=0, sticky=tk.S)

        self.quit_btn = ttk.Button(
            lf4,
            text="Quit",
            command=self.master.destroy)
        self.quit_btn.grid(row=0, column=6, sticky=tk.SE)

        # Container grid final adjustments
        self.grid_columnconfigure(0, weight=1)
        # We make this last row resizeable to accomodate the layout.
        self.rowconfigure(3, weight=1)

    def gui_update(self):
        if self.input1_filename.get() and self.input2_filename.get():
            tkhelpers.widget_recursive_enabler(self.combine_btn, True)
        else:
            tkhelpers.widget_recursive_enabler(self.combine_btn, False)

    def prompt_for_input_file(self, var):

        initial_filepath = var.get()
        initial_dir=os.path.dirname(initial_filepath)
        initial_file=os.path.basename(initial_filepath)

        filename = tk.filedialog.askopenfilename(
            title='Input File',
            filetypes = (('PDF files', '*.pdf'), ('All Files', '*.*')),
            initialdir=initial_dir,
            initialfile=initial_file
        )
        if filename:
            var.set(filename)
        
        self.after_idle(self.gui_update)

    def process_pdf(self):

        initial_dir=os.path.dirname(self.output_filename)
        initial_file=os.path.basename(self.output_filename)

        temp_output_filename = tk.filedialog.asksaveasfilename(
            title='Output File',
            defaultextension='.pdf',
            filetypes = (('PDF files', '*.pdf'),),
            initialdir=initial_dir,
            initialfile=initial_file
        )

        if not temp_output_filename:
            return

        self.output_filename = temp_output_filename

        if self.mode.get() == 0:
            pdfmanipulation.pdf_recto_verso(
                self.input1_filename.get(),
                self.input2_filename.get(),
                self.output_filename,
                reverse1=self.input1_reverse.get() != 0,
                reverse2=self.input2_reverse.get() != 0)

        elif self.mode.get() in [1, 2]:
            pdfmanipulation.pdf_append(
                self.input1_filename.get(),
                self.input2_filename.get(),
                self.output_filename,
                reverse=self.input1_reverse.get() != 0,
                append=self.mode.get()==1)


def report_callback_exception(self, exc, val, tb):
    showerror("Error", message=str(val))

if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("500x350")
    root.wm_resizable(0,0)

    tk.Tk.report_callback_exception = report_callback_exception

    app = Application(master=root)
    app.mainloop()
