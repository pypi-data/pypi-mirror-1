from setuptools import setup, find_packages

setup(
    name="getpaid.warehouse",
    version="0.2",
    author="Getpaid Community",
    author_email="getpaid-dev@googlegroups.com",
    description="Warehouse module for ecommerce framework",
    url="http://code.google.com/p/getpaid",
    classifiers = [
        "Framework :: Zope2",
        "Framework :: Zope3",
        "Framework :: Plone"
        ],
    packages=find_packages('src'),
    package_dir={'':'src'},
    namespace_packages=['getpaid'],
    include_package_data=True,
    install_requires = [ 'setuptools',
                         'getpaid.core',
                         ],
    zip_safe = False,
    )
