import tarfile
from tempfile import mkdtemp
from shutil import copy, rmtree
from os.path import abspath, join, isdir, isfile
from os import mkdir, remove

from paver.easy import *
from paver.setuputils import setup, find_packages

name = 'pysistence'
version = '0.3.0a4'
base_name = '%s-%s' % (name, version)
tarball_name = '%s.tar.gz' % base_name

options(
    setup=dict(
        name=name,
        packages=find_packages('source'),
        package_dir = {'':'source'},
        version=version,
        url="http://packages.python.org/pysistence",
        description='A set of functional data structures for Python',
        long_description='Pysistence is a library that seeks to bring functional data structures to Python.',
        author="Jason Baker",
        author_email="amnorvend@gmail.com",
        test_suite = 'nose.collector',
        tests_require = ['nose', 'coverage'],
        license='License :: OSI Approved :: MIT License',
        classifiers=[
            'Development Status :: 4 - Beta',
            'Intended Audience :: Developers',
            'Topic :: Software Development :: Libraries :: Python Modules',
            ]
        ),
)
setup()

@task
def doc():
    """Generate documentation."""
    sh('sphinx-build -a -E -W -b html -d build/doctrees source doc')
    zipdoc()
    
def zipdoc():
    sh('rm doc/pysistence-doc.zip', ignore_error=True)
    sh('zip -r pysistence-doc.zip ./*', cwd='doc')

@task
@cmdopts([
        ('build', 'b', 'build the documentation before displaying it')
        ])
def opendoc(options):
    """Open documentation in web browser"""
    if options.get('build'):
        doc()

    import webbrowser
    path = abspath('doc/index.html')
    webbrowser.open_new_tab(path)

