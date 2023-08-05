from distutils.core import setup

setup(name='pythk',
      version='0.1.1',
      description='Thinker\'s tool kit.',
      author='Thinker K.F. Li',
      author_email='thinker@branda.to',
      packages=['pythk'],
      package_dir={'pythk': '.'},
      requires=['pythk'],
      classifiers=['License :: OSI Approved :: BSD License',
                   'Programming Language :: Python',
		   'Topic :: Database',
		   'Topic :: Software Development :: Libraries'],
      license='BSD'
)
