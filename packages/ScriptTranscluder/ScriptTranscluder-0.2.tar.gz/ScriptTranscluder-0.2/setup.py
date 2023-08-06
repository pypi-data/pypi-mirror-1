from setuptools import setup, find_packages
import sys, os

version = '0.2'

index_doc = os.path.join(os.path.dirname(__file__), 'docs', 'index.txt')

setup(name='ScriptTranscluder',
      version=version,
      description="Transclude content via <script> tags",
      long_description=open(index_doc).read().strip(),
      classifiers=[
        "Development Status :: 4 - Beta",
        "Framework :: Paste",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Topic :: Internet :: WWW/HTTP :: WSGI",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        "Topic :: Text Processing :: Markup :: HTML",
      ],
      keywords='tranclude web application javascript',
      author='Ian Bicking',
      author_email='ianb@openplans.org',
      url='http://pypi.python.org/pypi/ScriptTranscluder',
      license='GPL',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
        'WebOb',
        'WebTest',
        'lxml>2.0alpha',
        'PasteScript',
        'httplib2',
      ],
      entry_points="""
      [paste.app_factory]
      main = scripttranscluder.wsgiapp:make_app
      """,
      )
