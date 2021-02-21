# pdf-multi-tools
GUI tools to modify PDF files, using tkinter, pypdf2 and pdftools

## how to test

    python pdf-multi-tools/pdfmultitools.pyw

## To compile

    python3 -m venv .venv


    .venv\Scripts\activate
 or
    source .venv/bin/activate
 
    pip install pdftools pyinstaller appdirs pyyaml
    pip intall pytest pylint
    pip install git+https://github.com/pmgagne/tkinterdnd2
    pyinstaller -F -w src\pdfmultitool.pyw --additional-hooks-dir=.
