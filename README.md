# pdf-multi-tools
GUI tools to modify PDF files, using tkinter, pypdf2 and pdftools

## To compile:

    python -m venv venv
    venv\Scripts\activate
    pip install -r requirements.txt
    pip install git+https://github.com/pmgagne/tkinterdnd2
    pyinstaller -F -w pdf-multi-tools\pdfmultitool.pyw --additional-hooks-dir=.
