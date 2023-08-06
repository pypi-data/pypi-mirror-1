from setuptools import setup, find_packages
import os

version = '0.11'

tests_require=['zope.testing']

def read(*rnames):
    return open(os.path.join(os.path.dirname(os.path.abspath(__file__)), *rnames)).read()

setup(name='quintagroup.themetemplate',
      version=version,
      description="Quintagroup theme template for Plone 3 with nested namespace",
      long_description=read("quintagroup", "themetemplate", "README.txt") + "\n" +
                       read("docs", "HISTORY.txt"),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='ZopeSkel theme template plone3 Quintagroup',
      author='Andriy Mylenkyy',
      author_email='support@quintagroup.com',
      url='http://svn.quintagroup.com/products/quintagroup.themetemplate',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['quintagroup'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'ZopeSkel',
          'PasteScript>=1.6.3',
          # -*- Extra requirements: -*-
      ],
      tests_require=tests_require,
      extras_require=dict(tests=tests_require),
      test_suite = 'quintagroup.themetemplate.tests.test_qthemedoc.test_suite',
      entry_points="""
          [paste.paster_create_template]
          qplone3_theme = quintagroup.themetemplate:qPlone3Theme

          [zopeskel.zopeskel_sub_template]
          skin_layer    = quintagroup.themetemplate.localcommands.subtemplates:SkinLayerSubTemplate
          css_resource = quintagroup.themetemplate.localcommands.subtemplates:CSSSubTemplate
          js_resource = quintagroup.themetemplate.localcommands.subtemplates:JSSubTemplate
          viewlet_order = quintagroup.themetemplate.localcommands.subtemplates:ViewletOrderSubTemplate
          viewlet_hidden = quintagroup.themetemplate.localcommands.subtemplates:ViewletHiddenSubTemplate
          import_zexps = quintagroup.themetemplate.localcommands.subtemplates:ImportSubTemplate

          [distutils.setup_keywords]
          theme_vars = quintagroup.themetemplate:assert_dict

          [egg_info.writers]
          theme_vars.txt = quintagroup.themetemplate:write_map

      # -*- Entry points: -*-
      """,
      setup_requires=['setuptools',],
      )
