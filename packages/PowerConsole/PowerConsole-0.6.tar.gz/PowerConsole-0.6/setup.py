from setuptools import setup, find_packages

import os
execfile(os.path.join("pwc", "release.py"))

setup(
    name=name,
    version=version,
    
    description=description,
    author=author,
    author_email=author_email,
    url=url,
    download_url=download_url,
    license=license,
    
    install_requires = [
        "pyparsing >= 1.5.1",
#        "filelike >= 0.3.2"
    ],
    scripts = ["ipwc.py"],
    #zip_safe=False,
    packages=find_packages(),
    #package_data = find_package_data(where='pwc', package='pwc'),
    namespace_packages = ['pwc'],
    entry_points = {
        'powerconsole.commands': [   
            'list = pwc.stdcmd:cmdList',
            'help = pwc.stdcmd:cmdHelp',
            'run = pwc.stdcmd:cmdRun'
        ],
        'powerconsole.help_providers': [   
            'python = pwc.stdcmd:helpPython',
            'builtin = pwc.stdcmd:helpBuiltin',
        ]
    },
    keywords = [
        # Use keywords if you'll be adding your package to the
        # Python Cheeseshop
        
    ],
    classifiers = [
        'Development Status :: 4 - Beta',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Interpreters',
        'Topic :: Software Development :: Libraries :: Python Modules',
        
    ],
#    test_suite = 'nose.collector',
    )
    
