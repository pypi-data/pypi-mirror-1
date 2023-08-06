from setuptools import setup, find_packages

setup(
    name = "ibanlib",
    version = "0.0.1",
    description="Library that supports developing applications that integrate the International Bank Account Number (IBAN).",
    author = "Hermann Himmelbauer",
    author_email = "dusty@qwer.tk",
    packages = ['ibanlib'],
    test_suite = "ibanlib.test",
    package_data = {
        # If any package contains *.txt or *.rst files, include them:
        '': ['*.txt'],
    }
)

