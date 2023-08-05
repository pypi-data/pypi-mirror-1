from setuptools import setup, find_packages

setup(
    name="hurry.file",
    version="1.0",
    packages=find_packages('src'),
    
    package_dir= {'':'src'},
    
    namespace_packages=['hurry'],
    package_data = {
    '': ['*.txt', '*.zcml'],
    },

    zip_safe=False,
    author='Infrae',
    author_email='faassen@infrae.com',
    description="""\
hurry.file is an advanced Zope 3 file widget which tries its best to behave
like other widgets, even when the form is redisplayed due to a validation
error. It also has built-in support for fast Apache-based file uploads
and downloads through Tramline.
""",
    license='BSD',
    keywords="zope zope3",
    classifiers = ['Framework :: Zope3'],
    install_requires=['setuptools'],
    )
