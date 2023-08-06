from setuptools import setup, find_packages

setup(
    name = "textindexng",
    version = "3.2.3",
    packages = find_packages('.'),
    package_dir = {'' : '.'},
    include_package_data = True,
    zip_safe=False,
    package_data = {'' : ['*.zcml', '*.sh']},
    author = 'Andreas Jung, ZOPYX Ltd. & Co KG, Tuebingen, Germany',
    author_email = 'info@zopyx.com',
    description = 'TextIndexNG3 core indexing engine',
    license = "ZPL",
    keywords = "Fulltext indexing",
    install_requires=['zopyx.textindexng3',
                      'zope.interface', 
                      'zope.component', 
                      'zope.app.catalog'],
)
