from setuptools import setup

setup(
    name = "ymsglib",
    version = "0.1",
    description = "Module implementing the yahoo messenger protocol v16.",
    long_description = """
        Auth part implemented from http://carbonize.co.uk/ymsg16.html
        Based on libyahoo2/libpurple/openymsg        
    """,
    author = "Daniel Anechitoaie",
    author_email='daniel dot anechitoaie at gmail dot com',
    url='http://code.google.com/p/ymsg/',
    
    # Description of the modules and packages in the distribution
    packages = ['ymsg'],
    
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Topic :: System :: Networking',
    ],      
    
    
)