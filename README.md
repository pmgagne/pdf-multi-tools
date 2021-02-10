# pdf-multi-tools
GUI tools to modify PDF files, using tkinter, pypdf2 and pdftools

## how to test

    python pdf-multi-tools/pdfmultitools.pyw

## To compile

    py -3.8 -m venv .venv
    .venv\Scripts\activate
    pip install pdftools pyinstaller
    pip install git+https://github.com/pmgagne/tkinterdnd2
    pyinstaller -F -w src\pdfmultitool.pyw --additional-hooks-dir=.
