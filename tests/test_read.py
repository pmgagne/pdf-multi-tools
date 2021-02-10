import pdfmanipulation
from PyPDF2 import PdfFileReader, PdfFileWriter

def read_content(file):
    f = open(file, "rb")
    r = PdfFileReader(f)
    content = [page.extractText().strip() for page in r.pages]
    f.close()
    return content

def test_read_contents():
    assert read_content('tests/split/even_001.pdf') == ["2"]
    assert read_content('tests/even.pdf') == ["2", "4", "6"]

def test_pdf_recto_verso(tmp_path):
    output = tmp_path / "test_pdf_recto_verso.pdf"

    pdfmanipulation.pdf_recto_verso(
        'tests/odd.pdf',
        'tests/even.pdf',
        output=output,
        reverse1=False,
        reverse2=False)
    assert read_content(output) == ["1", "2", "3", "4", "5", "6"]

    pdfmanipulation.pdf_recto_verso(
        'tests/odd.pdf',
        'tests/even.pdf',
        output=output,
        reverse1=True,
        reverse2=False)
    assert read_content(output) == ["5", "2", "3", "4", "1", "6"]

    pdfmanipulation.pdf_recto_verso(
        'tests/odd.pdf',
        'tests/even.pdf',
        output=output,
        reverse1=False,
        reverse2=True)
    assert read_content(output) == ["1", "6", "3", "4", "5", "2"]

def test_pdf_append(tmp_path):
    output = tmp_path / "test_pdf_append.pdf"

    pdfmanipulation.pdf_append(
        'tests/odd.pdf',
        'tests/even.pdf',
        output=output,
        reverse1=False,
        reverse2=False,
        append=True)
    assert read_content(output) == ["1", "3", "5", "2", "4", "6"]

    pdfmanipulation.pdf_append(
        'tests/odd.pdf',
        'tests/even.pdf',
        output=output,
        reverse1=True,
        reverse2=False,
        append=True)
    assert read_content(output) == ["5", "3", "1", "2", "4", "6"]

    pdfmanipulation.pdf_append(
        'tests/odd.pdf',
        'tests/even.pdf',
        output=output,
        reverse1=False,
        reverse2=True,
        append=True)
    assert read_content(output) == ["1", "3", "5", "6", "4", "2"]

    pdfmanipulation.pdf_append(
        'tests/odd.pdf',
        'tests/even.pdf',
        output=output,
        reverse1=False,
        reverse2=False,
        append=False)
    assert read_content(output) == ["2", "4", "6", "1", "3", "5"]

    pdfmanipulation.pdf_append(
        'tests/odd.pdf',
        'tests/even.pdf',
        output=output,
        reverse1=True,
        reverse2=False,
        append=False)
    assert read_content(output) == ["2", "4", "6", "5", "3", "1"]

    pdfmanipulation.pdf_append(
        'tests/odd.pdf',
        'tests/even.pdf',
        output=output,
        reverse1=False,
        reverse2=True,
        append=False)
    assert read_content(output) == ["6", "4", "2", "1", "3", "5"]

def test_pdf_merge_directory(tmp_path):
    output = tmp_path / "test_pdf_merge_directory.pdf"

    pdfmanipulation.pdf_merge_directory(
        ('tests/odd.pdf', 'tests/even.pdf'),
        output=output,
        reverse=False)
    assert read_content(output) == ["1", "3", "5", "2", "4", "6"]

    pdfmanipulation.pdf_merge_directory(
        ('tests/odd.pdf', 'tests/even.pdf'),
        output=output,
        reverse=True)
    assert read_content(output) == ["2", "4", "6", "1", "3", "5"]

def test_pdf_split(tmp_path):
    output = tmp_path / "test_pdf_split"
    output.mkdir()

    output_paths = pdfmanipulation.pdf_split(
        input='tests/odd.pdf',
        output_dir=output,
        reverse=False,
        dry_run=False)

    assert len(output_paths) == 3
    assert read_content(output / 'odd_001.pdf') == ["1"]
    assert read_content(output / 'odd_002.pdf') == ["3"]
    assert read_content(output / 'odd_003.pdf') == ["5"]

    assert read_content(output_paths[0]) == ["1"]
    assert read_content(output_paths[1]) == ["3"]
    assert read_content(output_paths[2]) == ["5"]

    output_paths = pdfmanipulation.pdf_split(
        input='tests/odd.pdf',
        output_dir=output,
        reverse=True,
        dry_run=False)

    assert len(output_paths) == 3
    assert read_content(output / 'odd_001.pdf') == ["5"]
    assert read_content(output / 'odd_002.pdf') == ["3"]
    assert read_content(output / 'odd_003.pdf') == ["1"]

    assert read_content(output_paths[0]) == ["5"]
    assert read_content(output_paths[1]) == ["3"]
    assert read_content(output_paths[2]) == ["1"]

def test_pdf_delete_page(tmp_path):
    output = tmp_path / "test_pdf_delete_page.pdf"

    pdfmanipulation.pdf_delete_page(
        input='tests/odd.pdf',
        output=output,
        pages=[1])
    assert read_content(output) == ["3", "5"]

    pdfmanipulation.pdf_delete_page(
        input='tests/odd.pdf',
        output=output,
        pages=[2,3])
    assert read_content(output) == ["1"]

    pdfmanipulation.pdf_delete_page(
        input='tests/odd.pdf',
        output=output,
        pages=[1, 2, 3])
    assert read_content(output) == []