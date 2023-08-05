from distutils.core import setup

setup(name='mez_xml',
      version='0.3',
      description='A template generator',
      long_description='''
      mez_xm is a template generator.
      It generates a Python template module for a XML or XHTML file.''',
      author='Thinker K.F. Li',
      author_email='thinker@branda.to',
      url='https://www.branda.to/mez_xml/',
      packages=['mez_xml'],
      package_dir={'mez_xml': '.'},
      classifiers=['License :: OSI Approved :: BSD License',
                   'Programming Language :: Python',
		   'Topic :: Internet :: WWW/HTTP :: Dynamic Content :: CGI Tools/Libraries',
		   'Topic :: Software Development :: Libraries'],
      license='BSD'
)
