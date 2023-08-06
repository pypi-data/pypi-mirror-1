from setuptools import setup, find_packages

long_description = (open('README.txt').read()
                    + '\n\n' +
                    open('CHANGES.txt').read())

setup(
    name='grokproject',
    version='0.7',
    author='Grok Team',
    author_email='grok-dev@zope.org',
    url='https://launchpad.net/grok',
    download_url='svn://svn.zope.org/repos/main/grokproject/trunk#egg=grokproject-dev',
    description='Script that sets up a grok project directory, installs Zope 3 and grok and creates a template for a grok application.',
    long_description=long_description,
    license='ZPL',

    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=['PasteScript>=1.3',],
    entry_points="""
    [console_scripts]
    grokproject = grokproject:main
    [paste.paster_create_template]
    grokproject = grokproject:GrokProject
    """,
)
