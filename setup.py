from setuptools import find_packages, setup

setup(
    name='pdfmultitool',
    version="0.0.5.0",
    description='Pdf manipulation helper',
    author='Philippe Gagné',
    packages=find_packages(
        'src',
        exclude=['*.tests', '*.tests.*', 'tests.*', 'tests', 'tkhelpers.py', 'pdfmultitool.pyw']
    ),
    package_dir={'': 'src'},
    python_requires='>=3.8,<4',
    entry_points = {
        'console_scripts': ['pdfmultitool=src.pdfmultitool:main'],
    }
)
