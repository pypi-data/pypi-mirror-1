from setuptools import setup, find_packages

setup(
    name = "MakoLang",
    version = "0.1",
    packages = find_packages(),
    entry_points = """
    [babel.extractors]
    makolang = makolang:extract_makolang
    """,
    install_requires = ["Mako>=0.1.8","Babel>=0.8.1"],
    
    author = "Paul Colomiets",
    author_email = "pc@gafol.net",
    description = "This package adds preprocessor to mako"
        " for convenient syntax of gettext strings,"
        " and babel extractor to process such templates.",
    license = "MIT",
    keywords = "mako templates gettext i18n l10n",
    url = "http://www.mr-pc.kiev.ua/en/projects/MakoLang",
    )
