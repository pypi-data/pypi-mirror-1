import ez_setup
ez_setup.use_setuptools()
from setuptools import setup

setup(name="clipartbrowser",
        description="A gtk browser for the Open Clipart Library",
        author="Greg Steffensen",
        author_email="greg.steffensen@gmail.com",
        url="http://code.google.com/p/clipartbrowser",
        version="0.5a1",
        license = 'GPL',
        keywords = 'clipart art clipartbrowser ocal images',
        packages = ['clipartbrowser'],

        include_package_data = True,

        entry_points = {
            'gui_scripts': ['clipartbrowser = clipartbrowser.browser:run']
        },

        install_requires = ['pyparsing', 'pygtk>=2.6', 'lxml>=1.0', 'pysqlite']

)
