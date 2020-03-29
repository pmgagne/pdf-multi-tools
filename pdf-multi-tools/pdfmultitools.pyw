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
import tkinterdnd2

def is_files_exists(files):
    """Return True if at least one file (in files) already exists."""
    for file in files:
        if os.path.isfile(file):
            return True
    return False

class Application(ttk.Frame):
    mode_defs = bidict.Bidict({int(0): 'zip', int(1): 'append', int(2): 'prepend', int(3): 'split'})

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
        parameters = {'general': {}, 'zip':{}, 'append':{}, 'prepend':{}, 'split':{}}

        parameters['general']['confirm'] = True
        
        parameters['zip']['input1_reverse'] = False
        parameters['zip']['input2_reverse'] = True

        parameters['append']['input1_reverse'] = False
        parameters['append']['input2_reverse'] = False

        parameters['prepend']['input1_reverse'] = False
        parameters['prepend']['input2_reverse'] = False

        parameters['split']['input1_reverse'] = False
        parameters['split']['input2_reverse'] = False

        return parameters

    def gui_mode_switch(self, previous_mode:str, next_mode:str):
        """Set widget state based on active parameters"""

        if previous_mode and previous_mode != next_mode:
            # Save previous mode params
            self.parameters[previous_mode]['input1_reverse'] = self.input1_reverse.get()!=0
            self.parameters[previous_mode]['input2_reverse'] = self.input2_reverse.get()!=0
            self.parameters['general']['confirm'] = self.confirm_output.get()

        self.input1_reverse.set(self.parameters[next_mode]['input1_reverse'])
        self.input2_reverse.set(self.parameters[next_mode]['input2_reverse'])
        self.confirm_output.set(self.parameters['general']['confirm'])

        self.mode = next_mode

    def create_widgets(self):

        # Input file 1
        self.lf1 = ttk.LabelFrame(self, text='File 1:', padding=(12,6))
        self.lf1.grid(row=0, column=0, sticky=tk.EW, padx=6, pady=12)
        self.lf1.grid_columnconfigure(0, minsize=100, weight=1)

        filename = ttk.Entry(
            master=self.lf1, 
            text="Input File 1", 
            textvariable=self.input1_filename)
        filename.grid(row=0, column=0, sticky=tk.EW)
        filename.drop_target_register(tkinterdnd2.DND_FILES, tkinterdnd2.DND_TEXT)
        filename.dnd_bind('<<Drop>>', lambda event: self.drop(event, self.input1_filename))

        filename_chooser = ttk.Button(
            master=self.lf1, 
            text="\N{Horizontal Ellipsis}", # aka "..."
            command=lambda:self.prompt_for_input_file(self.input1_filename) )
        filename_chooser.grid(row=0, column=1)

        input1_reverse = ttk.Checkbutton(
            master=self.lf1, 
            text="Reverse", 
            variable=self.input1_reverse)
        input1_reverse.grid(row=1, column=0, sticky=tk.W)

        # Input file 2
        self.lf2 = ttk.LabelFrame(self, text='File 2:', padding=(12,6))
        self.lf2.grid(row=1, column=0, sticky=tk.EW, padx=6, pady=6)
        self.lf2.grid_columnconfigure(0, minsize=100, weight=1)


        filename = ttk.Entry(
            master=self.lf2, 
            text="Input File 2", 
            textvariable=self.input2_filename)
        filename.grid(row=0, column=0, sticky=tk.EW)
        filename.drop_target_register(tkinterdnd2.DND_FILES, tkinterdnd2.DND_TEXT)
        filename.dnd_bind('<<Drop>>', lambda event: self.drop(event, self.input2_filename))
        
        filename_chooser = ttk.Button(
            master=self.lf2, 
            text="\N{Horizontal Ellipsis}", # aka "..."
            command=lambda:self.prompt_for_input_file(self.input2_filename) )
        filename_chooser.grid(row=0, column=1)

        input2_reverse = ttk.Checkbutton(
            master=self.lf2, 
            text="Reverse", 
            variable=self.input2_reverse)
        input2_reverse.grid(row=1, column=0, sticky=tk.W)

        # Output file
        lf3 = ttk.LabelFrame(self, text='Output:', padding=(12,6))
        lf3.grid(row=2, column=0, sticky=tk.EW, padx=6, pady=6)
        lf3.grid_columnconfigure(0, minsize=100, weight=1)

        lf3_buttons = ttk.LabelFrame(lf3, text="Mode:", padding=(12,6))
        lf3_buttons.grid(row=1, column=0, sticky=tk.W)
        
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
        ttk.Radiobutton(
            lf3_buttons, 
            text='Separate', 
            variable=self.mode_selection, 
            value = 3,
            command=self.gui_update).grid(row=0,column=3)

        ttk.Checkbutton(
            lf3,
            text="Confirm Result", 
            variable=self.confirm_output).grid(row=2, column=0, sticky=tk.W)

        lf4 = ttk.Frame(self)
        lf4.grid(row=3, column=0, sticky=tk.S+tk.EW, padx=12, pady=12)
        lf4.columnconfigure(6, weight=1)
        
        self.process_btn = ttk.Button(
            master=lf4,
            text='Process',
            command=self.process_pdf)
        self.process_btn.grid(row=0, column=0, sticky=tk.S)

        self.quit_btn = ttk.Button(
            lf4,
            text="Quit",
            command=self.master.destroy)
        self.quit_btn.grid(row=0, column=6, sticky=tk.SE)

        # Container grid final adjustments
        self.grid_columnconfigure(0, weight=1)
        # We make this last row resizeable to accomodate the layout.
        self.rowconfigure(3, weight=1)

    def drop(self, event, variable):
        if event.data:
            # event.data is a list of filenames as one string;
            # if one of these filenames contains whitespace characters
            # it is rather difficult to reliably tell where one filename
            # ends and the next begins; the best bet appears to be
            # to count on tkdnd's and tkinter's internal magic to handle
            # such cases correctly; the following seems to work well
            # at least with Windows and Gtk/X11
            files = self.tk.splitlist(event.data)
            variable.set(files[0])
            self.after_idle(self.gui_update)
        return event.action

    def gui_update(self):
        previous_mode = self.mode
        next_mode = self.mode_defs[self.mode_selection.get()]

        self.gui_mode_switch(previous_mode=previous_mode, next_mode=next_mode)

        #  Gui enablers.
        if self.mode == 'split':
            # Split mode only requires input1_filename
            if self.input1_filename.get():
                tkhelpers.widget_recursive_enabler(self.process_btn, True)
            else:
                tkhelpers.widget_recursive_enabler(self.process_btn, False)

            tkhelpers.widget_recursive_enabler(self.lf2, False)
        else:
            # Other modes need both filenames.
            if self.input1_filename.get() and self.input2_filename.get():
                tkhelpers.widget_recursive_enabler(self.process_btn, True)
            else:
                tkhelpers.widget_recursive_enabler(self.process_btn, False)

            tkhelpers.widget_recursive_enabler(self.lf2, True)

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

    def prompt_for_output_path(self, output_is_dir=False):
        initial_dir=os.path.dirname(self.last_outputfile)
        initial_file=os.path.basename(self.last_outputfile)

        if not output_is_dir:
            output_path = tk.filedialog.asksaveasfilename(
                title='Output File',
                defaultextension='.pdf',
                filetypes = (('PDF files', '*.pdf'),),
                initialdir=initial_dir,
                initialfile=initial_file
            )
        else:
            output_path = tk.filedialog.askdirectory(
                title='Output File',
                initialdir=initial_dir,
            )

        return output_path

    def confirm_result(self, filepath):
        result = tkinter.messagebox.askyesno(
            "Result",
            "Successfully Done.\n"
            "Do you want to open the resulting file?""")

        if result:
            subprocess.call(('cmd /c start "" "'+ filepath +'"') if os.name is 'nt' else ('open' if sys.platform.startswith('darwin') else 'xdg-open', filepath))

    def process_pdf(self):
        output_path = ""
        
        if self.mode == 'zip':
            output_path = self.prompt_for_output_path()
            if not output_path:
                return

            pdfmanipulation.pdf_recto_verso(
                self.input1_filename.get(),
                self.input2_filename.get(),
                output_path,
                reverse1=self.input1_reverse.get() != 0,
                reverse2=self.input2_reverse.get() != 0)

        elif self.mode in ('append', 'prepend'):
            output_path = self.prompt_for_output_path()
            if not output_path:
                return

            pdfmanipulation.pdf_append(
                self.input1_filename.get(),
                self.input2_filename.get(),
                output_path,
                reverse1=self.input1_reverse.get() != 0,
                reverse2=self.input2_reverse.get() != 0,
                append=self.mode=='append')

        elif self.mode == 'split':
            output_path = self.prompt_for_output_path(output_is_dir=True)
            if not output_path:
                return

            # Call split in dry-run to only get output file names. Reverse is not important here.
            output_files = pdfmanipulation.pdf_split(
                self.input1_filename.get(), 
                output_path, 
                dry_run=True)

            if is_files_exists(output_files):
                ok_to_overwrite = tkinter.messagebox.askyesno(
                    title="Split files", 
                    message="The split operation will overite some files.\nContinue ?")
                if not ok_to_overwrite:
                    return

            # Do the actual split operation
            pdfmanipulation.pdf_split(
                self.input1_filename.get(), 
                output_path, 
                reverse=self.input1_reverse.get() != 0)
        else:
            assert(False)

        # Offer to open the result file or directory
        self.last_outputfile = output_path
        if self.confirm_output.get():
            self.confirm_result(filepath=output_path)

def report_callback_exception(self, exc, val, tb):
    tkinter.messagebox.showerror("Error", message=str(val))

if __name__ == "__main__":
    root = tkinterdnd2.Tk()
    root.geometry("500x400")
    root.wm_resizable(0,0)

    #tk.Tk.report_callback_exception = report_callback_exception

    app = Application(master=root)
    app.mainloop()
