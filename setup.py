from setuptools import setup, find_packages

setup(
    name='django-debug-toolbar-line-profiling',
    version='0.7.2',
    description='A panel for django-debug-toolbar that integrates ' +
                'information from line_profiler',
    long_description=open('README.rst').read(),
    author='Mykhailo Keda',
    author_email='mriynuk@gmail.com',
    url='https://github.com/mikekeda/django-debug-toolbar-line-profiler',
    download_url='https://pypi.python.org/pypi/django-debug-toolbar-line-profiling',
    license='BSD',
    packages=find_packages(exclude=('tests', 'example')),
    install_requires=[
        'django>=2.2'
        'django-debug-toolbar>=2.0',
        'line_profiler>=1.0b3',
        'six>=1.10',
    ],
    include_package_data=True,
    zip_safe=False,                 # because we're including static files
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
