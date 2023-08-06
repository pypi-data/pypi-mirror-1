import sys
try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

setup(
    name = "html2text",
    version = "2.37",
    description = "Turn HTML into equivalent Markdown-structured text.",
    author = "Aaron Swartz",
    author_email = "me@aaronsw.com",
    url='http://www.aaronsw.com/2002/html2text/',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Affero General Public License v3',
      ],
    license='GNU GPL 3',
    py_modules=['html2text']
)
