from pathlib import Path

from setuptools import find_packages, setup

setup(
    name='django-debug-toolbar-line-profiling',
    version='0.8.0',
    description='A panel for django-debug-toolbar that integrates information from line_profiler',
    long_description=Path('README.rst').read_text(encoding='locale'),
    author='Mykhailo Keda',
    author_email='mriynuk@gmail.com',
    url='https://github.com/mikekeda/django-debug-toolbar-line-profiler',
    download_url='https://pypi.python.org/pypi/django-debug-toolbar-line-profiling',
    license='BSD',
    packages=find_packages(exclude=('tests', 'example')),
    install_requires=[
        'django-debug-toolbar>=4.0.0',
        'line_profiler>=3.4.0',
    ],
    include_package_data=True,
    zip_safe=False,  # because we're including static files
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
