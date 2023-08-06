from setuptools import setup, find_packages
import os


setup(
    name='pycleaner',
    version='0.2.0',
    author='Michael Carter',
    author_email='CarterMichael@gmail.com',
    license='MIT License',
    description='Remove ~ and .pyc recursively',
    long_description='',
    packages= find_packages(),
    zip_safe = False,
    install_requires = [
        # "event >= 0.3"
    ],
    
    entry_points = '''    
        [console_scripts]
        pycleaner = pycleaner.clean:main
    ''',
    
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],        
)
