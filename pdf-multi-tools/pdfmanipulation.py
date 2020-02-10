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
    reverse2: bool = False,
):
    """
    Zip pages of input1 and input2 in one output file. Useful for putting
    even and odd pages together in one document.
    :param input1: first input file
    :param input2: second input file
    :param output: output file
    :param delete: if true the input files will be deleted after zipping

    """

    outputfile = open(output, "wb")
    try:
        f1, f2 = open(input1, "rb"), open(input2, "rb")
        r1, r2 = PdfFileReader(f1), PdfFileReader(f2)
        writer = PdfFileWriter()
        pages1 = [page for page in r1.pages]
        pages2 = [page for page in r2.pages]

        if reverse1:
            pages1 = reversed(pages1)

        if reverse2:
            pages2 = reversed(pages2)

        for p1, p2 in zip(pages1, pages2):
            writer.addPage(p1)
            writer.addPage(p2)

        writer.write(outputfile)

        f1.close()
        f2.close()
    except FileNotFoundError as e:
        print(e.strerror + ": " + e.filename)
    finally:
        outputfile.close()

def pdf_append(
    input1: str,
    output: str,
    reverse1: bool = False,
    append: bool = True
):
    """
    Zip pages of input1 and input2 in one output file. Useful for putting
    even and odd pages together in one document.
    :param input1: first input file
    :param input2: second input file
    :param output: output file
    :param delete: if true the input files will be deleted after zipping

    """

    outputfile = tempfile.TemporaryFile()
    try:
        f1, f2 = open(input1, "rb"), open(output, "rb"),
        r1, r2 = PdfFileReader(f1), PdfFileReader(f2)
        writer = PdfFileWriter()

        # TODO: pages1 = r1.pages ?
        pages1 = [page for page in r1.pages]
        pages2 = [page for page in r2.pages]

        if reverse1:
            pages1 = reversed(pages1)

        if append:
            for p2 in pages2:
                writer.addPage(p2)

            for p1 in pages1:
                writer.addPage(p1)
        else:
            for p1 in pages1:
                writer.addPage(p1)

            for p2 in pages2:
                writer.addPage(p2)

        writer.write(outputfile)

        f1.close()
        f2.close()
        
        shutil.copy2(outputfile, output)

    except FileNotFoundError as e:
        print(e.strerror + ": " + e.filename)

        