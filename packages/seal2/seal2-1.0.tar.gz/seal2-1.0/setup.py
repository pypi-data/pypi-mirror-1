from setuptools import setup, Extension

version = "1.0"

setup(name='seal2',
      version=version,
      description="SEAL2 encryption",
      long_description=open("README.txt").read()+open("CHANGES.txt").read(),
      classifiers=[
          "Intended Audience :: Developers",
          "Operating System :: OS Independent",
          "Programming Language :: Python",
          "Topic :: Security :: Cryptography",
          "Topic :: Software Development :: Libraries :: Python Modules",
      ], 
      keywords=["crypto", "SEAL2"],
      author='Wichert Akkerman - Jarn',
      author_email='info@jarn.com',
      license='GPL',
      ext_modules = [
          Extension(
              "seal2",
              [
                  "src/seal2.c",
                  "src/seal2module.c",
              ],
          ),
          ],
      zip_safe=True,
      tests_require = "nose >= 0.10.0b1",
      test_suite = "nose.collector",
      )
