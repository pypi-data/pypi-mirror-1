from setuptools import setup, find_packages

setup (
    name = "TurboClearsilver",
    version = "0.2",
    description="Clearsilver plugin for TurboGears and Buffet",
    author="John Hampton",
    author_email="pacopablo@asylumware.com",
    url="http://embassy.asylumware.com/projects/turboclearsilver",
    
    classifiers = [
    'Development Status :: 3 - Alpha',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'License :: OSI Approved :: MIT License',
    'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    
    packages=find_packages(),
    zip_safe=True,
    entry_points = """
    [python.templating.engines]
    clearsilver = turboclearsilver.cssupport:TurboClearsilver
    """
    )

