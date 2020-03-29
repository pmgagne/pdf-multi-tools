# pdf-multi-tools
GUI tools to modify PDF files, using tkinter, pypdf2 and pdftools

## how to test

    python pdf-multi-tools/pdfmultitools.pyw

## To compile

    py -3.7 -m venv venv
    venv\Scripts\activate
    pip install -r requirements.txt
    pip install git+https://github.com/pmgagne/tkinterdnd2
    pyinstaller -F -w pdf-multi-tools\pdfmultitools.pyw --additional-hooks-dir=.
