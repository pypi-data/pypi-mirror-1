import os
from setuptools import setup, find_packages, Extension

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

setup(name='vudo.cmf',
      version = '0.2',
      description='Content management framework.',
      long_description=read('README.txt'),
      keywords = "zope vudo repoze bfg cmf",
      classifiers = [
          'Development Status :: 4 - Beta',
          'Environment :: Web Environment',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: Zope Public License',
          'Programming Language :: Python',
          'Natural Language :: English',
          'Operating System :: OS Independent',
          'Topic :: Internet :: WWW/HTTP',
          'Framework :: Zope3'],
      license='BSD',
      packages=find_packages('src'),
      package_dir = {'': 'src'},
      namespace_packages=['vudo', ],
      install_requires=['setuptools',
                        'zope.dublincore',
                        'repoze.bfg',
                        'repoze.formapi',
                        'repoze.bfg.skins',
                        'repoze.bfg.httprequest',
                        'plone.transforms',
                        'Markdown',
                        ],  
      include_package_data=True,
      zip_safe=False,
      entry_points="""
      # -*- Entry points: -*-
      [vudo.skin]
      cmf=vudo.cmf:provide_skin [skin]
      """,
      extras_require={
          "skin": "vudo.skinsetup",
          }
      )
