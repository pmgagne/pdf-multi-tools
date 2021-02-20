#!/usr/bin/env python

import sys, os, subprocess
import os.path
from enum import IntEnum

import tkinter as tk
from tkinter import ttk
import tkinter.filedialog
import tkinter.messagebox


import pdfmanipulation
import tkhelpers
import tkinterdnd2

class Operation(IntEnum):
    NONE = 0
    ZIP = 1
    APPEND = 2
    PREPEND = 3
    SPLIT = 4
    DIR_COMBINE = 5
    PAGE_DELETE = 6
    PAGE_ROTATE = 7
    METADATA_EDIT = 8

def is_files_exists(files):
    """Return True if at least one file (in files) already exists."""
    for file in files:
        if os.path.isfile(file):
            return True
    return False

def pdf_files_in_directory(dir_path):
    """Return a list of all PDF files in dir_path."""
    pdf_files = []

    if os.path.isfile(dir_path):
        dir_path = os.path.dirname(dir_path)

    files = os.scandir(dir_path)
    for file in files:
        if os.path.isfile(file)  \
                and os.path.splitext(file.name)[1].upper() == '.PDF':
            pdf_files.append(file.path)

    pdf_files.sort()
    return pdf_files

def get_page_numbers(pageRange):
    # parse a page range (i.e: 1,2,5,56-100,241) and return its 
    # integer equivalent
    pageIndex = 0
    inDigit = False
    inNums2 = False
    nums = ""
    nums2 = ""
    pageNumbers = []
 
    while(pageIndex < len(pageRange)):
        if(pageRange[pageIndex].isdigit()):
            inDigit = True
        else:
            inDigit = False
 
        if(inDigit):
            if(inNums2 == False):
                nums += pageRange[pageIndex]
            else:
                nums2 += pageRange[pageIndex]
        else:
            if(nums != "" and pageRange[pageIndex] == "," and inNums2 == False):
                pageNumbers.append(int(nums))
                nums = ""
            elif(nums != "" and pageRange[pageIndex] == "-"):
                inNums2 = True
            elif(nums2 != "" and inNums2):
                for x in range(int(nums), int(nums2)+1):
                    pageNumbers.append(x)
                nums = ""
                nums2 = ""
                inNums2 = False
            elif((nums != "" and pageRange[pageIndex] != ",")
                or (nums != "" and pageRange[pageIndex] != "-")):
                pageNumbers.append(int(nums))
                nums = ""
        pageIndex += 1
 
    # DO THIS IF NUMBERS ARE LEFT OVER FROM THE ABOVE LOOP ^
    if(nums != "" and nums2 != ""):
        for x in range(int(nums), int(nums2)+1):
            pageNumbers.append(x)
    elif(nums != ""):
        pageNumbers.append(int(nums))
 
    return pageNumbers

class Application(ttk.Frame):
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

        self.input1_filename = tk.StringVar()
        self.input1_reverse = tk.IntVar()
        self.input1_page_range = tk.StringVar()
        self.input1_argument = tk.DoubleVar()

        self.input2_filename = tk.StringVar()
        self.input2_reverse = tk.IntVar()

        self.mode = Operation.ZIP
        self.mode_selection = tk.IntVar()
        self.mode_selection.set(self.mode.value)
        self.confirm_output = tk.IntVar()

        self.create_widgets()  
        self.gui_mode_switch(previous_mode=Operation.NONE, next_mode=Operation.ZIP)
        self.after_idle(self.gui_update)

    def create_parameters(self):
        parameters = {
            'general': {}, 
            Operation.ZIP:{}, 
            Operation.APPEND:{}, 
            Operation.PREPEND:{}, 
            Operation.SPLIT:{}, 
            Operation.DIR_COMBINE:{},
            Operation.PAGE_DELETE:{},
            Operation.PAGE_ROTATE:{}}

        parameters['general']['confirm'] = True
        
        parameters[Operation.ZIP]['input1_reverse'] = False
        parameters[Operation.ZIP]['input2_reverse'] = True
        parameters[Operation.ZIP]['output_path'] = ""

        parameters[Operation.APPEND]['input1_reverse'] = False
        parameters[Operation.APPEND]['input2_reverse'] = False
        parameters[Operation.APPEND]['output_path'] = ""

        parameters[Operation.PREPEND]['input1_reverse'] = False
        parameters[Operation.PREPEND]['input2_reverse'] = False
        parameters[Operation.PREPEND]['output_path'] = ""

        parameters[Operation.SPLIT]['input1_reverse'] = False
        parameters[Operation.SPLIT]['input2_reverse'] = False
        parameters[Operation.SPLIT]['output_path'] = ""

        parameters[Operation.DIR_COMBINE]['input1_reverse'] = False
        parameters[Operation.DIR_COMBINE]['input2_reverse'] = False
        parameters[Operation.DIR_COMBINE]['output_path'] = ""

        parameters[Operation.PAGE_DELETE]['input1_reverse'] = False
        parameters[Operation.PAGE_DELETE]['input2_reverse'] = False
        parameters[Operation.PAGE_DELETE]['output_path'] = ""

        parameters[Operation.PAGE_ROTATE]['input1_reverse'] = False
        parameters[Operation.PAGE_ROTATE]['input2_reverse'] = False
        parameters[Operation.PAGE_ROTATE]['output_path'] = ""

        return parameters

    def gui_mode_switch(self, previous_mode:Operation, next_mode:Operation):
        """Set widget state based on active parameters"""

        if previous_mode != Operation.NONE and previous_mode != next_mode:
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
        self.lf1.grid(row=0, column=0, sticky=tk.EW, padx=6, pady=6)
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

        self.input1_reverse_checkbox = ttk.Checkbutton(
            master=self.lf1, 
            text="Reverse", 
            variable=self.input1_reverse)
        self.input1_reverse_checkbox.grid(row=1, column=0, sticky=tk.W)

        argument_frame = tk.Frame(master=self.lf1)
        argument_frame.grid(row=2, column=0, sticky=tk.W)

        l1 = ttk.Label(argument_frame, text="Pages: ")
        l1.grid(row=0, column=0, sticky=tk.W)

        self.page_range1 = ttk.Entry(
            master=argument_frame,
            text="",
            textvariable=self.input1_page_range)
        self.page_range1.grid(row=0, column=1, sticky=tk.W)

        l2 = ttk.Label(argument_frame, text="  Argument: ")
        l2.grid(row=0, column=2, sticky=tk.W)

        self.argument1 = ttk.Entry(
            master=argument_frame,
            text="",
            textvariable=self.input1_argument)
        self.argument1.grid(row=0, column=3, sticky=tk.W)

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
        lf3 = ttk.LabelFrame(self, text='Operation:', padding=(12,6))
        lf3.grid(row=2, column=0, sticky=tk.EW, padx=6, pady=6)
        
        ttk.Radiobutton(
            lf3, 
            text='Recto/Verso', 
            variable=self.mode_selection, 
            value = Operation.ZIP.value,
            command=self.gui_update).grid(row=0, column=0, padx=1, sticky=tk.W)
        ttk.Radiobutton(
            lf3, 
            text='Append',
            variable=self.mode_selection,
            value = Operation.APPEND.value,
            command=self.gui_update).grid(row=0, column=1, padx=1, sticky=tk.W)
        ttk.Radiobutton(
            lf3, 
            text='Prepend', 
            variable=self.mode_selection, 
            value = Operation.PREPEND.value,
            command=self.gui_update).grid(row=0, column=2, padx=1, sticky=tk.W)
        ttk.Radiobutton(
            lf3, 
            text='Separate', 
            variable=self.mode_selection, 
            value = Operation.SPLIT.value,
            command=self.gui_update).grid(row=0, column=3, padx=1, sticky=tk.W)
        ttk.Radiobutton(
            lf3, 
            text='Dir Combine', 
            variable=self.mode_selection, 
            value = Operation.DIR_COMBINE.value,
            command=self.gui_update).grid(row=1, column=0, padx=1, sticky=tk.W)
        ttk.Radiobutton(
            lf3, 
            text='Page Delete', 
            variable=self.mode_selection, 
            value = Operation.PAGE_DELETE.value,
            command=self.gui_update).grid(row=1, column=1, padx=1, sticky=tk.W)
        ttk.Radiobutton(
            lf3, 
            text='Page Rotate', 
            variable=self.mode_selection, 
            value = Operation.PAGE_ROTATE.value,
            command=self.gui_update).grid(row=1, column=2, padx=1, sticky=tk.W)

        ttk.Checkbutton(
            lf3,
            text="Confirm Result",
            variable=self.confirm_output).grid(row=2, column=0, sticky=tk.W, pady=12, padx=1)

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
        next_mode = self.mode_selection.get()

        self.gui_mode_switch(previous_mode=previous_mode, next_mode=next_mode)

        #  Gui enablers.
        if self.mode in [Operation.SPLIT, Operation.DIR_COMBINE, Operation.PAGE_DELETE, Operation.PAGE_ROTATE]:
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

        # Enable page selector
        if self.mode in [Operation.PAGE_DELETE, Operation.PAGE_ROTATE]:
            self.page_range1.state(['!disabled'])
            self.input1_reverse_checkbox.state(['disabled'])
        else:
            self.page_range1.state(['disabled'])
            self.input1_reverse_checkbox.state(['!disabled'])

        if self.mode in [Operation.PAGE_ROTATE]:
            self.argument1.state(['!disabled'])
        else:
            self.argument1.state(['disabled'])

    def prompt_for_input_file(self, var):

        initial_filepath = var.get()
        initial_dir=os.path.dirname(initial_filepath)
        initial_file=os.path.basename(initial_filepath)

        dir_select = self.mode == Operation.DIR_COMBINE

        if not dir_select:
            filename = tk.filedialog.askopenfilename(
                master=self,
                title='Input File',
                filetypes = (('PDF files', '*.pdf'), ('All Files', '*.*')),
                initialdir=initial_dir,
                initialfile=initial_file
            )
        else:
            filename = tk.filedialog.askdirectory(
                master=self,
                title='Input Directory',
                initialdir=initial_dir
            )

        if filename:
            var.set(filename)
        
        self.after_idle(self.gui_update)

    def prompt_for_output_path(self, output_is_dir=False, initial_path=None):
        initial_dir=os.path.dirname(initial_path)
        initial_file=os.path.basename(initial_path)

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
            subprocess.call(('cmd /c start "" "'+ filepath +'"') if os.name == 'nt' else ('open' if sys.platform.startswith('darwin') else 'xdg-open', filepath))

    def process_pdf(self):
        output_path = ""

        try:
            last_outputfile = self.parameters[self.mode]['output_path']

            if self.mode == Operation.ZIP:
                output_path = self.prompt_for_output_path(initial_path=last_outputfile)
                if not output_path:
                    return

                pdfmanipulation.pdf_recto_verso(
                    self.input1_filename.get(),
                    self.input2_filename.get(),
                    output_path,
                    reverse1=self.input1_reverse.get() != 0,
                    reverse2=self.input2_reverse.get() != 0)

            elif self.mode in (Operation.APPEND, Operation.PREPEND):
                output_path = self.prompt_for_output_path(
                    initial_path=self.last_outputfile)
                if not output_path:
                    return

                pdfmanipulation.pdf_append(
                    self.input1_filename.get(),
                    self.input2_filename.get(),
                    output_path,
                    reverse1=self.input1_reverse.get() != 0,
                    reverse2=self.input2_reverse.get() != 0,
                    append=self.mode == Operation.APPEND)

            elif self.mode == Operation.SPLIT:
                output_path = self.prompt_for_output_path(
                    output_is_dir=True,
                    initial_path=last_outputfile)

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
                        message="The split operation will overide some files.\nContinue ?")
                    if not ok_to_overwrite:
                        return

                # Do the actual split operation
                pdfmanipulation.pdf_split(
                    self.input1_filename.get(), 
                    output_path, 
                    reverse=self.input1_reverse.get() != 0)
            
            elif self.mode == Operation.DIR_COMBINE:
                files = pdf_files_in_directory(self.input1_filename.get())
                if not files:
                    tkinter.messagebox.showwarning(title='pdfmultitools', message='No PDF files found.')
                    return

                output_path = self.prompt_for_output_path(
                    output_is_dir=False,
                    initial_path=last_outputfile)

                if not output_path:
                    return

                pdfmanipulation.pdf_merge_directory(
                    files,
                    output_path,
                    reverse=self.input1_reverse.get() != 0
                )

            elif self.mode == Operation.PAGE_DELETE:
                output_path = self.prompt_for_output_path(
                    initial_path=last_outputfile)
                if not output_path:
                    return

                pages = get_page_numbers(self.input1_page_range.get())

                pdfmanipulation.pdf_delete_page(
                    self.input1_filename.get(),
                    output_path,
                    pages=pages)

            elif self.mode == Operation.PAGE_ROTATE:
                angle=self.input1_argument.get()
                if angle % 90 != 0:
                    tkinter.messagebox.showerror("Error", message="Angle must be multiple of 90°")
                    return
                
                output_path = self.prompt_for_output_path(
                    initial_path=last_outputfile)
                if not output_path:
                    return

                pages = get_page_numbers(self.input1_page_range.get())

                pdfmanipulation.pdf_rotate_page(
                    self.input1_filename.get(),
                    output_path,
                    angle=self.input1_argument.get(),
                    pages=pages)

            else:
                assert(False)

            # Offer to open the resulting file or directory
            if self.confirm_output.get():
                self.confirm_result(filepath=output_path)

            # Memorise last output file path to serve as initial path next time,
            # except for split mode. 
#            if self.mode != Operation.SPLIT:
            self.parameters[self.mode]['output_path'] = output_path

        except Exception as e:
            message = str(e)
            tkinter.messagebox.showwarning(title='Pdf Multi Tool', message=message)


def report_callback_exception(self, exc, val, tb):
    tkinter.messagebox.showerror("Error", message=str(val))

if __name__ == "__main__":
    root = tkinterdnd2.Tk()
    root.geometry("500x400")
    root.wm_resizable(0,0)

    #tk.Tk.report_callback_exception = report_callback_exception

    app = Application(master=root)
    app.mainloop()
