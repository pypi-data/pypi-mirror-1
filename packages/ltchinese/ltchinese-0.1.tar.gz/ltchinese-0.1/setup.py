from distutils.core import setup
import sys

sys.path.append('ltchinese')
import ltchinese

from email.utils import parseaddr
author,email = parseaddr(ltchinese.__author__)

setup(
    name='ltchinese',
    version='0.1',
    author=author,
    author_email=email,
    url=ltchinese.__url__,
    download_url=ltchinese.__url__,
    description='A library of utilities for the Chinese language (pinyin, zhuyin, encodings, phonetics, etc.) from http://lost-theory.org.',
    long_description=ltchinese.__doc__,
    keywords='chinese pinyin zhuyin encoding gb2312 utf8 unicode phonetics mandarin language web',
    license='MIT License',
    packages=['ltchinese'],
    package_data={
        'ltchinese': ['ltchinese/data/*']
    },
    platforms='any',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'License :: OSI Approved :: MIT License',
        'Topic :: Text Processing :: Linguistic',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Localization',
    ],
)
