from setuptools import setup, find_packages
import os

setup(name='megrok.layout',
      version='0.3',
      description="A layout component package for zope3 and Grok.",
      long_description = open(os.path.join("megrok/layout", "README.txt")
                              ).read() + "\n",
      classifiers=[
          "Framework :: Zope3",
          "Programming Language :: Python",
          "Programming Language :: Zope",
          "Intended Audience :: Developers",
          "Development Status :: 4 - Beta",
          "Topic :: Software Development :: Libraries :: Python Modules",
          ],
      keywords='grok layout zope3 pagelet theming',
      author='Souheil Chelfouh',
      author_email='trollfot@gmail.com',
      url='http://pypi.python.org/pypi/megrok.layout',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['megrok'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
	  'grok',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
