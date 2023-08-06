from setuptools import setup

long_description = """This script splits Malayalam words into letters.
Ref: http://tinyurl.com/3v729s

Usage:

  python mlsplit.py input.txt [input.txt-out.txt]
"""

setup(
    name='mlsplit',
    version='0.1.2',
    author='Baiju M',
    author_email='baiju.m.mail@gmail.com',
    description='Split Malayalam words into letters',
    long_description=long_description,
    keywords = "pypi console tools",
    classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Utilities',
        ],
    url='http://pypi.python.org/pypi/mlsplit',
    license='GPLv3',
    scripts=['mlsplit.py'],
    package_data={
        '': ['*.txt']
        },
    zip_safe=False,
    )
