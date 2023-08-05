from setuptools import setup, find_packages

setup(
    name = "textindexng",
    version = "3.2.0",
    packages = find_packages('.'),
    package_dir = {'' : '.'},
    include_package_data = True,
    author = 'Andreas Jung, ZOPYX Ltd. & Co KG, Tuebingen, Germany',
    author_email = 'info@zopyx.com',
    description = 'TextIndexNG3 core indexing engine',
    license = "ZPL",
    keywords = "Fulltext indexing",
)
