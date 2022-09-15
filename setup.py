import sys
from setuptools import setup, find_packages
import f3tch

tests_require = [
    "pytest==7.1.3"
]

dev_require = [
    *tests_require,
    "matplotlib==3.5.2",
    "numpy==1.22.3",
    "openshift==0.13.1",
    "openshift_client==1.0.16",
    "pandas==1.4.2"
]

install_requires = [
    "pip",
    "setuptools"
]

def long_description():
    with open('README.md', encoding='utf-8') as f:
        return f.read()

# bdist_wheel
extras_require = {
    'dev': dev_require,
    'test': tests_require
}

setup(
    name='f3tch',
    version=f3tch.__version__,
    description=f3tch.__doc__.strip(),
    long_description=long_description(),
    long_description_content_type='text/markdown',
    url="",
    download_url=f'https://github.com/f3tch/f3tch/archive/{f3tch.__version__}.tar.gz',
    author=f3tch.__author__,
    author_email='sharat.saurabh@gmail.com',
    license=f3tch.__licence__,
    packages=find_packages(include=['f3tch', 'f3tch.*']),
    entry_points={
        'console_scripts': [
            'f3tch = f3tch.__main__:main'
        ],
    },
    python_requires='>=3.9',
    extras_require=extras_require,
    install_requires=install_requires,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3 :: Only',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development',
        'Topic :: Terminals',
        'Topic :: Utilities'
    ],
    project_urls={
        'GitHub': 'https://github.com/sakhoury/f3tch',
    },
    data_files=[
    ]
)
