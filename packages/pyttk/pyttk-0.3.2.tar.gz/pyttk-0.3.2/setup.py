from distutils.core import setup
import ttk

setup(
    name='pyttk',
    version=ttk.__version__,
    author='Guilherme Polo',
    author_email='ggpolo@gmail.com',
    url='http://code.google.com/p/python-ttk',
    description='Ttk Python wrapper',
    classifiers = [
        'Programming Language :: Python :: 2.5',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3'
        ],
    py_modules=['ttk']
)
