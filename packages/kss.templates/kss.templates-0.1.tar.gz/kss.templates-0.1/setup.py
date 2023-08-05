from setuptools import setup, find_packages

version = '0.1'

setup(name='kss.templates',
      version=version,
      description="Templates for creating KSS plugins",
      long_description="""
kss.templates provides templates for development with KSS. It
currently has templates for creating plugins. These generate the
server side and client side code (including heavily commented
Javascript code).
""",
      classifiers=[
        "Development Status :: 3 - Alpha",
        "Framework :: Paste",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: JavaScript",
        "Topic :: Software Development :: Code Generators",
        ],
      keywords='skeleton kss plugin',
      author='KSS Project',
      author_email='kss-devel@codespeak.net',
      url='http://kssproject.org',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['kss'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'PasteScript'
      ],
      entry_points={
        'paste.paster_create_template': [
            'kss_plugin=kss.templates.util:KSSPluginTemplate',
            'kss_zope_plugin=kss.templates.util:KSSZopePluginTemplate',
            ],
        },
)
