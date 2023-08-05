import ez_setup
ez_setup.use_setuptools()

from setuptools import setup

setup(
    name = "pyahoolib",
    version = "0.2",
    description = "Module implementing the yahoo messenger protocol.",
    long_description = """
        Had this code lieing around. Has the nasty yahoo autentification 
        worked out, it's class based and it has a bunch of examples. 
        You can you do simple bots and other basic stuff with it - check 
        the examples.
    """,
    author = "Maries Ionel Cristian",
    author_email='ionel dot mc at gmail dot com',
    
    # Description of the modules and packages in the distribution
    packages = ['yahoo'],
    
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Topic :: System :: Networking',
    ],      
    
    
)