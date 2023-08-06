from distutils.core import setup

setup(
    name = "obfuscate",
    py_modules=["obfuscate"],
    version = "0.2.2a",
    author = "Steven D'Aprano",
    author_email = "steve+python@pearwood.info",
    url = 'http://pypi.python.org/pypi/obfuscate',
    keywords = ["obfuscate", "encryption", "cipher", "text"],
    description = "Obfuscate text with classic encryption algorithms",
    long_description = """\
Obfuscation and classical encryption algorithms
-----------------------------------------------

Obfuscate and unobfuscate text using classical encryption algorithms.

Includes
 - Caesar cipher, rot13, rot5, rot18, rot47
 - atbash
 - Playfair, Playfair6 and Playfair16
 - Railfence (encryption only)
 - Keyword
 - Affine
 - Vigenere
 - frob (xor)
 - and others.

Requires Python 2.5 or 2.6.
""",
    license = 'MIT',  # apologies for the American spelling
    classifiers = [
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.5",
        "Programming Language :: Python :: 2.6",
        "Environment :: Other Environment",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Security :: Cryptography",
        "Topic :: Text Processing",
        "License :: OSI Approved :: MIT License",
        ],
    )

