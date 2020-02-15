#!/usr/bin/env python

import sys, os, subprocess
import os.path

import tkinter as tk
from tkinter import ttk
import tkinter.filedialog
import tkinter.messagebox

import bidict
import pdfmanipulation
import tkhelpers


class Application(ttk.Frame):
    mode_defs = bidict.Bidict({int(0): 'zip', int(1): 'append', int(2): 'prepend'})

    def __init__(self, master=None):
        super().__init__(master)
        self.pack(expand=1, fill='both')
        self.master.title('pdf multi tool')
        
        # Not resizeable.
        #ttk.Sizegrip().pack(side='right')

        # Each mode has a different set of parameters.
        self.parameters = self.create_parameters()

        self.last_inputfile1 = ""
        self.last_inputfile2 = ""
        self.last_outputfile = ""

        self.input1_filename = tk.StringVar()
        self.input1_reverse = tk.IntVar()

        self.input2_filename = tk.StringVar()
        self.input2_reverse = tk.IntVar()

        self.mode = 'zip'
        self.mode_selection = tk.IntVar()
        self.mode_selection.set(self.mode_defs.inverse[self.mode][0])
        self.confirm_output = tk.IntVar()

        self.create_widgets()        
        self.gui_mode_switch(previous_mode="", next_mode='zip')
        self.after_idle(self.gui_update)

    def create_parameters(self):
        parameters = {'general': {}, 'zip':{}, 'append':{}, 'prepend':{}}

        parameters['general']['confirm'] = True
        
        parameters['zip']['input1_reverse'] = False
        parameters['zip']['input2_reverse'] = True

        parameters['append']['input1_reverse'] = False
        parameters['append']['input2_reverse'] = False

        parameters['prepend']['input1_reverse'] = False
        parameters['prepend']['input2_reverse'] = False

        return parameters

    def gui_mode_switch(self, previous_mode:str, next_mode:str):
        """Set widget state based on active parameters"""
        if previous_mode and previous_mode != next_mode:
            # Save previous mode params
            self.parameters[previous_mode]['input1_reverse'] = self.input1_reverse.get()!=0
            self.parameters[previous_mode]['input2_reverse'] = self.input2_reverse.get()!=0

        self.input1_reverse.set(self.parameters[next_mode]['input1_reverse'])
        self.input2_reverse.set(self.parameters[next_mode]['input2_reverse'])

        self.mode = next_mode

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
            variable=self.mode_selection, 
            value = 0,
            command=self.gui_update).grid(row=0,column=0)
        ttk.Radiobutton(
            lf3_buttons, 
            text='Append',
            variable=self.mode_selection,
            value = 1,
            command=self.gui_update).grid(row=0,column=1)
        ttk.Radiobutton(
            lf3_buttons, 
            text='Prepend', 
            variable=self.mode_selection, 
            value = 2,
            command=self.gui_update).grid(row=0,column=2)

        ttk.Checkbutton(
            lf3,
            text="Confirm Result", 
            variable=self.confirm_output).grid(row=1, column=1, sticky=tk.W)

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
        previous_mode = self.mode
        next_mode = self.mode_defs[self.mode_selection.get()]

        self.gui_mode_switch(previous_mode=previous_mode, next_mode=next_mode)

        if self.input1_filename.get() and self.input2_filename.get():
            tkhelpers.widget_recursive_enabler(self.combine_btn, True)
        else:
            tkhelpers.widget_recursive_enabler(self.combine_btn, False)

    def prompt_for_input_file(self, var):

        initial_filepath = var.get()
        initial_dir=os.path.dirname(initial_filepath)
        initial_file=os.path.basename(initial_filepath)

        filename = tk.filedialog.askopenfilename(
            master=self,
            title='Input File',
            filetypes = (('PDF files', '*.pdf'), ('All Files', '*.*')),
            initialdir=initial_dir,
            initialfile=initial_file
        )

        if filename:
            var.set(filename)
        
        self.after_idle(self.gui_update)

    def prompt_for_output_file(self):

        initial_dir=os.path.dirname(self.last_outputfile)
        initial_file=os.path.basename(self.last_outputfile)

        filename = tk.filedialog.asksaveasfilename(
            title='Output File',
            defaultextension='.pdf',
            filetypes = (('PDF files', '*.pdf'),),
            initialdir=initial_dir,
            initialfile=initial_file
        )

        return filename

    def confirm_result(self, filepath):
        result = tkinter.messagebox.askyesno(
            "Result",
            "Successfully Done.\n"
            "Do you want to open the resulting file?""")

        if result:
            subprocess.call(('cmd /c start "" "'+ filepath +'"') if os.name is 'nt' else ('open' if sys.platform.startswith('darwin') else 'xdg-open', filepath))

    def process_pdf(self):
        output_filename = self.prompt_for_output_file()
        if not output_filename:
            return

        if self.mode == 'zip':
            pdfmanipulation.pdf_recto_verso(
                self.input1_filename.get(),
                self.input2_filename.get(),
                output_filename,
                reverse1=self.input1_reverse.get() != 0,
                reverse2=self.input2_reverse.get() != 0)

        elif self.mode.get() in ('append', 'prepend'):
            pdfmanipulation.pdf_append(
                self.input1_filename.get(),
                self.input2_filename.get(),
                output_filename,
                reverse1=self.input1_reverse.get() != 0,
                reverse2=self.input2_reverse.get() != 0,
                append=self.mode=='append')

        self.last_outputfile = output_filename
        if self.confirm_output.get():
            self.confirm_result(filepath=output_filename)

def report_callback_exception(self, exc, val, tb):
    tkinter.messagebox.showerror("Error", message=str(val))

if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("500x350")
    root.wm_resizable(0,0)

    #tk.Tk.report_callback_exception = report_callback_exception

    app = Application(master=root)
    app.mainloop()
