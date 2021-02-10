from typing import Union

import os
import tempfile
import shutil
from PyPDF2 import PdfFileReader, PdfFileWriter

def pdf_recto_verso(
    input1: str,
    input2: str,
    output: str,
    reverse1: bool = False,
    reverse2: bool = False):
    """
    Zip pages of input1 and input2 in one output file. Useful for putting
    even and odd pages together in one document.
    :param input1: first input file
    :param input2: second input file
    :param output: output file
    :param reverse1: reverse page order of input1 if True
    :param reverse2: reverse page order of input2 if True
    """

    outputfile = tempfile.NamedTemporaryFile()

    f1, f2 = open(input1, "rb"), open(input2, "rb")
    r1, r2 = PdfFileReader(f1), PdfFileReader(f2)
    writer = PdfFileWriter()

    if reverse1:
        pages1 = reversed(r1.pages)
    else:
        pages1 = r1.pages

    if reverse2:
        pages2 = reversed(r2.pages)
    else:
        pages2 = r2.pages

    for p1, p2 in zip(pages1, pages2):
        writer.addPage(p1)
        writer.addPage(p2)

    writer.write(outputfile)

    f1.close()
    f2.close()

    outputfile.seek(0)
    f2 = open(output, "wb")
    shutil.copyfileobj(outputfile, f2)
    f2.close()
    outputfile.close()

def pdf_append(
    input1: str,
    input2: str,
    output: str,
    reverse1: bool = False,
    reverse2: bool = False,
    append: bool = True):
    """
    Append or prepend input1 pages to input2, then save to output.
    :param input1: first input file
    :param input2: second input file
    :param output: output file
    :param reverse: reverse page order of input1 if True
    :param append: append if True, prepend if False
    """

    outputfile = tempfile.NamedTemporaryFile()

    f1, f2 = open(input1, "rb"), open(input2, "rb")
    r1, r2 = PdfFileReader(f1), PdfFileReader(f2)
    writer = PdfFileWriter()

    if reverse1:
        pages1 = reversed(r1.pages)
    else:
        pages1 = r1.pages

    if reverse2:
        pages2 = reversed(r2.pages)
    else:
        pages2 = r2.pages

    if append:
        for p1 in pages1:
            writer.addPage(p1)

        for p2 in pages2:
            writer.addPage(p2)
    else:
        for p2 in pages2:
            writer.addPage(p2)

        for p1 in pages1:
            writer.addPage(p1)

    writer.write(outputfile)

    f1.close()
    f2.close()
    
    outputfile.seek(0)
    f2 = open(output, "wb")
    shutil.copyfileobj(outputfile, f2)
    f2.close()
    outputfile.close()

def pdf_merge_directory(
    input_files,
    output: str,
    reverse: bool = False):
    """
    Append or prepend input1 pages to input2, then save to output.
    :param input: file list
    :param output: output file
    :param reverse: reverse page order of input1 if True
    """
    outputfile = tempfile.NamedTemporaryFile()
    writer = PdfFileWriter()

    if reverse:
        input_files = reversed(input_files)

    for input_file in input_files:
        f = open(input_file, "rb")
        r = PdfFileReader(f)
        for p in r.pages:
            writer.addPage(p)
        writer.write(outputfile)
        f.close()

    outputfile.seek(0)
    f2 = open(output, "wb")
    shutil.copyfileobj(outputfile, f2)
    f2.close()
    outputfile.close()

def pdf_split(
    input: str,
    output_dir: str,
    reverse: bool = False,
    dry_run=False
):
    """
    Split the input file in multiple output files.
    pdf_split will overwrite pre-existing files.

    :param input: name of the input file
    :param output_dir: output directory
    :param reverse:  reverse page order of input if True
    :param dry_run: if true, don't actually write output files.
    :return list of output file 
    """

    output_paths = []
    with open(input, "rb") as inputfile:
        reader = PdfFileReader(inputfile)
        page_count = len(reader.pages)

    filename_prefix = os.path.splitext(os.path.basename(input))[0]
    output_prefix = os.path.join(output_dir, filename_prefix)
    output_paths = ["{}_{:03d}.pdf".format(output_prefix, page+1) for page in range(page_count)]

    if not dry_run:
        with open(input, "rb") as inputfile:
            reader = PdfFileReader(inputfile)

            if reverse:
                pages = reversed(reader.pages)
            else:
                pages = reader.pages

            for page, output in zip(pages, output_paths):
                outputfile = open(output, "wb")
                writer = PdfFileWriter()
                writer.addPage(page)
                writer.write(outputfile)
                outputfile.close()

            inputfile.close()

    return output_paths

def pdf_delete_page(
    input1: str,
    output: str,
    pages):
    """Zip pages of input1 and input2 in one output file. Useful for putting
    even and odd pages together in one document.
    :param input1: input file
    :param output: output file
    :param pages: List of pages number to remove (1-based index)
    """
    outputfile = tempfile.NamedTemporaryFile()

    f1 = open(input1, "rb")
    r1 = PdfFileReader(f1)
    writer = PdfFileWriter()

    for page_no, page in enumerate(r1.pages):
        if page_no+1 not in pages:
            writer.addPage(page)

    writer.write(outputfile)

    f1.close()

    outputfile.seek(0)
    f2 = open(output, "wb")
    shutil.copyfileobj(outputfile, f2)
    f2.close()
    outputfile.close()

def pdf_rotate_page(
    input1: str,
    output: str,
    angle: float,
    pages):
    """Zip pages of input1 and input2 in one output file. Useful for putting
    even and odd pages together in one document.
    :param input1: input file
    :param output: output file
    :param angle: rotation angle in degrees 
    :param pages: List of pages number to remove (1-based index) or None
                  to rotate all
    """

    outputfile = tempfile.NamedTemporaryFile()

    f1 = open(input1, "rb")
    r1 = PdfFileReader(f1)
    writer = PdfFileWriter()

    for page_no, page in enumerate(r1.pages):
        if pages is None or page_no+1 in pages:
            writer.addPage(page.rotateClockwise(angle))
        else:
            writer.addPage(page)

    writer.write(outputfile)
    f1.close()

    outputfile.seek(0)
    f2 = open(output, "wb")
    shutil.copyfileobj(outputfile, f2)
    f2.close()
    outputfile.close()