#!/usr/bin/env python

# Based upon https://github.com/stlehmann/pdftools/blob/master/pdfzip.py


import sys
import argparse
from pdftools import pdf_zip
from pdftools.parseutil import parentparser

import tkinter as tk
from tkinter import ttk
import tkinter.filedialog

class Application(ttk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.pack(expand=1, fill='both')
        self.master.title('pdfzip')
        self.create_widgets()
        
        # Not resizeable.
        #ttk.Sizegrip().pack(side='right')

    def create_widgets(self):

        # Input file 1
        lf1 = ttk.LabelFrame(self, text='File 1:', padding=(12,6))
        lf1.grid(row=0, column=0, sticky=tk.EW, padx=6, pady=12)
        lf1.grid_columnconfigure(0, minsize=100, weight=1)

        self.input1_filename = tk.StringVar()
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

        # Input file 2
        lf2 = ttk.LabelFrame(self, text='File 2:', padding=(12,6))
        lf2.grid(row=1, column=0, sticky=tk.EW, padx=6, pady=6)
        lf2.grid_columnconfigure(0, minsize=100, weight=1)

        self.input2_filename = tk.StringVar()
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

        self.input2_reverse = tk.IntVar()
        self.input2_reverse.set(1)
        input2_reverse = ttk.Checkbutton(
            master=lf2, 
            text="Reverse", 
            variable=self.input2_reverse)
        input2_reverse.grid(row=1, column=0, sticky=tk.W)

        # Output file
        lf3 = ttk.LabelFrame(self, text='Output:', padding=(12,6))
        lf3.grid(row=2, column=0, sticky=tk.EW, padx=6, pady=6)
        lf3.grid_columnconfigure(0, minsize=100, weight=1)

        self.output_filename = tk.StringVar()
        filename = ttk.Entry(
            master=lf3, 
            text="Output file", 
            textvariable=self.output_filename)
        filename.grid(row=0, column=0, sticky=tk.EW)
        
        filename_chooser = ttk.Button(
            master=lf3, 
            text="\N{Horizontal Ellipsis}", # aka "..."
            command=lambda:self.prompt_for_output_file(self.output_filename) )
        filename_chooser.grid(row=0, column=1)

        lf4 = ttk.Frame(self)
        lf4.grid(row=3, column=0, sticky=tk.S+tk.EW, padx=12, pady=12)
        lf4.columnconfigure(6, weight=1)
        
        self.combine_btn = ttk.Button(
            master=lf4,
            text='Zip',
            command=self.zip_pdf)
        self.combine_btn.grid(row=0, column=0, sticky=tk.S)

        self.quit_btn = ttk.Button(
            lf4,
            text="Exit",
            command=self.master.destroy)
        self.quit_btn.grid(row=0, column=6, sticky=tk.SE)

        # Container grid final adjustments
        self.grid_columnconfigure(0, weight=1)
        # We make this last row resizeable to accomodate the layout.
        self.rowconfigure(3, weight=1)


    def prompt_for_input_file(self, var):
        filename = tk.filedialog.askopenfilename(
            title='Input File',
            filetypes = (('PDF files', '*.pdf'), ('All Files', '*.*'))
        )
        if filename:
            var.set(filename)
            
    def prompt_for_output_file(self, var):
        filename = tk.filedialog.asksaveasfilename(
            title='Output File',
            defaultextension='.pdf',
            filetypes = (('PDF files', '*.pdf'),)
        )
        if filename:
            var.set(filename)

    def zip_pdf(self):
        pdf_zip(self.input1_filename.get(),
                self.input2_filename.get(),
                self.output_filename.get(),
                delete=False,
                revert=self.input2_reverse.get() != 0)


def process_arguments(args):
    parser = argparse.ArgumentParser(
        parents=[parentparser],
        description="Zip the pages of two documents in one output file.")

    # input1
    parser.add_argument('input1',
                        type=str,
                        help='first inputfile')
    # input2
    parser.add_argument('input2',
                        type=str,
                        help='second inputfile')
    # output
    parser.add_argument('-o',
                        '--output',
                        type=str,
                        default=None,
                        help='filename of the output file',
                        required=True)
    # delete
    parser.add_argument('-d',
                        '--delete',
                        action='store_true',
                        help='delete input files after merge')
    # revert
    parser.add_argument('-r',
                        '--revert',
                        action='store_true',
                        help='revert the pages of second input file')
    return parser.parse_args(args)


if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("500x300")
    root.wm_resizable(0,0)
    app = Application(master=root)
    app.mainloop()
