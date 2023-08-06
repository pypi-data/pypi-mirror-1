from setuptools import setup, find_packages
import os
setup(
    name='pycleaner',
    version='1.0',
    author='Michael Carter',
    author_email='CarterMichael@gmail.com',
    url='http://www.orbited.org/projects.html',
    license='MIT License',
    description='A command to recurisvely delete .pyc files',
    long_description='After installing pycleaner, execute the command pycleaner in any directory to recursively delete all .pycs in that dir.',
    packages=[
        'pycleaner'
    ],
    zip_safe = True,
    
    entry_points = '''    
        [console_scripts]
        pycleaner = pycleaner.clean:main
    ''',
    
    classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development'
    ],        
)

