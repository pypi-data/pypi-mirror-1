import tarfile
from tempfile import mkdtemp
from shutil import copy, rmtree
from os.path import abspath, join, isdir, isfile
from os import mkdir, remove

from paver.easy import *
from paver.setuputils import setup, find_packages

name = 'pysistence'
version = '0.2.0'
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
        tests_require = ['nose'],
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
@needs('generate_setup', 'minilib', 'distutils.command.sdist')
def sdist():
    """Generate a source distribution."""
    tempdir = mkdtemp()
    tarball_path = join('dist', tarball_name)
    archive = tarfile.open(tarball_path)
    print 'Adding setup.py and paver-minilib.zip'
    try:
        archive.extractall(tempdir)
        sub_dir = join(tempdir, base_name)
        copy('setup.py', sub_dir)
        copy('paver-minilib.zip', sub_dir)
    finally:
        archive.close()
    archive = tarfile.open(tarball_path, 'w:gz')
    archive.add(sub_dir, arcname='pysistence')
    archive.close()
    rmtree(tempdir)

@task
def clean():
    sh('rm -rf build')
    sh('rm setup.py')
    sh('rm paver-minilib.zip')

@task
def doc():
    """Generate documentation."""
    sh('sphinx-build -a -E -W -b html -d build/doctrees source build/html')

@task
@cmdopts([
        ('build', 'b', 'build the documentation before displaying it')
        ])
def opendoc(options):
    """Open documentation in web browser"""
    if options.get('build'):
        doc()

    import webbrowser
    path = abspath('build/html/index.html')
    webbrowser.open_new_tab(path)
