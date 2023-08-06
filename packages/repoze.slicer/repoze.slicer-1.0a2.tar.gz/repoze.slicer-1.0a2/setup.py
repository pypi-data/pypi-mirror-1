from setuptools import setup, find_packages

README = open("README.txt").read()
CHANGES = open("CHANGES.txt").read()

setup(name="repoze.slicer",
      version="1.0a2",
      description="WSGI middleware to filter HTML responses",
      long_description='\n\n'.join([README, "Changelog\n=========\n", CHANGES]),
      classifiers=[
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Internet :: WWW/HTTP :: WSGI",
        ],
      keywords='wsgi html transformation',
      author="Wichert Akkerman",
      author_email="repoze-dev@lists.repoze.org",
      url="http://www.repoze.org",
      license="BSD",
      packages=find_packages(),
      include_package_data=False,
      namespace_packages=["repoze"],
      zip_safe=True,
      install_requires=[
          "WSGIFilter",
          "lxml",
          "setuptools",
          ],
      test_suite = "repoze.slicer.tests",
      entry_points = """\
      [paste.filter_app_factory]
      slicer = repoze.slicer:Slicer.paste_deploy_middleware
      """
      )

