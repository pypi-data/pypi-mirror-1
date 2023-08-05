from distutils.core import setup

setup(name='ez_web',
      version='0.1',
      description='A light-weight WEB framework for Python',
      long_description='''
      ez_web is a light-weight WEB framework.  It is desinged
      for modification.  Programmer can start to modify it
      in a short time.''',
      author='Thinker K.F. Li',
      author_email='thinker@branda.to',
      url='https://opensvn.csie.org/traccgi/PumperWeb/wiki/ez_web',
      packages=['ez_web'],
      package_dir={'ez_web': '.'},
      requires=['pythk', 'ez_xml', 'mod_python'],
      classifiers=['License :: OSI Approved :: BSD License',
                   'Programming Language :: Python',
		   'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
		   'Topic :: Software Development'],
      license='BSD'
)
