from ez_setup import use_setuptools
use_setuptools()

from setuptools import setup, find_packages

from benri import __VERSION__

setup(name='benri',
    version=__VERSION__, 
    author='Mikael Hoegqvist',
    author_email='hoegqvist@zib.de',
    url='',
    download_url='',
    description='A REST-service creation framework.',
    license='',
    long_description="""Convenience framework for REST service creation. Uses
                        Paste for many basic tasks.""",
    packages = find_packages(),
    install_requires = [
    'Paste>=1.4',
    'PasteScript>=1.3.5',
    'selector>=0.8.11',
#    'static>=0.3.3',
    ],    
    entry_points = """
    [paste.paster_create_template]
    benri=benri.templates:BenriTemplate
    """,
     classifiers=[
    'Development Status :: 4 - Beta',
    'Environment :: Web Environment',
    'Intended Audience :: Developers',
    'Programming Language :: Python',
    'Topic :: Internet :: WWW/HTTP',
    'Topic :: Software Development :: Libraries',
    ],
    zip_safe = False,
    )

