from distutils.core import setup

setup(name='ez_xml',
      version='0.1.3',
      description='A template generator',
      long_description='''
      ez_xm is a template generator.
      It provides simple functions to direct the generator how to generator a
      Python template code for a XML or XHTML file.''',
      author='Thinker K.F. Li',
      author_email='thinker@branda.to',
      url='https://opensvn.csie.org/traccgi/PumperWeb/wiki/ez_xml',
      packages=['ez_xml'],
      package_dir={'ez_xml': '.'},
      requires=['pythk'],
      classifiers=['License :: OSI Approved :: BSD License',
                   'Programming Language :: Python',
		   'Topic :: Internet :: WWW/HTTP :: Dynamic Content :: CGI Tools/Libraries',
		   'Topic :: Software Development :: Libraries'],
      license='BSD'
)
