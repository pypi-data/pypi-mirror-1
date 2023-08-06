from distutils.core import setup
setup(
    name="Mallet",
    version="0.1.5",
    packages=[
        'mallet',
    ],
    scripts=[
        'scripts/mallet-add-client.py',
        'scripts/mallet-build-image.py',
    ],

    #install_requires=['simplejson>=2.0'],

    package_data={
        # If any package contains *.txt or *.rst files, include them:
      #  '': ['*.txt', '*.rst'],
        # And include any *.msg files found in the 'hello' package, too:
     #   'hello': ['*.msg'],
    },

    # metadata for upload to PyPI
    author="Tobias McNulty",
    author_email="tobias@caktusgroup.com",
    description="This package provides scripts for building and maintaining"\
                  " Debian-based virtual servers for web application hosting.",
    license="BSD",
    keywords="virtual machine server hosting management script",
    url="http://bitbucket.org/tobias.mcnulty/mallet",

    # could also include long_description, download_url, classifiers, etc.
)
