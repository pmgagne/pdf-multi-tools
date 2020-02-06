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
        ttk.Sizegrip().pack(side='right')

    def create_widgets(self):

        lf1 = ttk.LabelFrame(self, text='File 1:')
        lf1.pack(side="top", expand=1, fill='x')

        self.params1 = self.create_input_file_widget(lf1)

        lf2 = ttk.LabelFrame(self, text='File 2:')
        lf2.pack(side="top", expand=1, fill='x')

        self.params2 = self.create_input_file_widget(lf2)

        lf3 = ttk.LabelFrame(self, text='Output:')
        lf3.pack(side="top", expand=1, fill='x')

        self.params3 = self.create_output_file_widget(lf3)

        self.hi_there = ttk.Button(self)
        self.hi_there["text"] = "Zip"
        self.hi_there["command"] = self.zip_pdf
        self.hi_there.pack(side="left")

        self.quit = ttk.Button(self, text="Exit",
                              command=self.master.destroy)
        self.quit.pack(side="right")

    def create_input_file_widget(self, master):
        filename_var = tk.StringVar()
        filename = ttk.Entry(
            master=master, 
            text="File", 
            textvariable=filename_var)
        filename.pack(side='left', expand=1, fill='x')
        
        filename_chooser = ttk.Button(
            master, 
            text="\N{Horizontal Ellipsis}", # aka "..."
            command=lambda:self.prompt_for_input_file(filename_var) )
        filename_chooser.pack(side='right')

        params = {'path': filename_var}
        return params

    def create_output_file_widget(self, master):
        filename_var = tk.StringVar()
        filename = ttk.Entry(
            master=master, 
            text="File", 
            textvariable=filename_var)
        filename.pack(side='left', expand=1, fill='x')
        
        filename_chooser = ttk.Button(
            master, 
            text="\N{Horizontal Ellipsis}", # aka "..."
            command=lambda:self.prompt_for_output_file(filename_var) )
        filename_chooser.pack(side='right')

        params = {'path': filename_var}
        return params

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
        pdf_zip(self.params1['path'].get(),
                self.params2['path'].get(),
                self.params3['path'].get(),
                delete=False,
                revert=False)


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
    root.geometry("500x250")
    root.wm_resizable(0,0)
    app = Application(master=root)
    app.mainloop()
