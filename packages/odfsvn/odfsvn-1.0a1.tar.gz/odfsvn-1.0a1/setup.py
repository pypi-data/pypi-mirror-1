from setuptools import setup, find_packages
import os

version = "1.0a1"

setup(name              = "odfsvn",
      version           = version,
      description       = "Manage ODF files in SubVersioN",
      long_description  = open("README.txt").read() + "\n" + \
                          open(os.path.join("docs", "INSTALL.txt")).read(),
      classifiers       = [
          "Intended Audience :: End Users/Desktop",
          "License :: OSI Approved :: GNU General Public License (GPL)",
          "Programming Language :: Python",
          "Topic :: Office/Business :: Office Suites",
          "Topic :: Text Editors :: Word Processors",
          ],
      keywords          = "ODF SVN",
      author            = "Wichert Akkerman - Simplon",
      author_email      = "wichert@simplon.biz",
      url               = "http://www.sourceforge.net/projects/odfsvn/",
      license           = "GPL3",
      packages          = find_packages(exclude=["examples", "tests"]),
      include_package_data=True,
      zip_safe         = True,
      install_requires = [ ],
      tests_require    = "nose >=0.10.0b1",
      test_suite       = "nose.collector",
      entry_points     = {
          "console_scripts" : [
              "odfsvn = odfsvn.scripts.main:main",
              ],
      },
      )
