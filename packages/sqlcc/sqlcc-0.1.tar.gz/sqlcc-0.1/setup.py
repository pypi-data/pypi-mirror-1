from distutils.core import setup

setup(name='sqlcc',
      version='0.1',
      description='Python SQL Command Composer.',
      long_description='''
      sqlcc is a Python SQL Command Composer
      It make you composing sql commands without quote & composing
      strings.  You can working in totally Python style, never
      embed SQL command in string, again.''',
      author='Thinker K.F. Li',
      author_email='thinker@branda.to',
      packages=['sqlcc'],
      package_dir={'sqlcc': '.'},
      requires=['pythk'],
      classifiers=['License :: OSI Approved :: BSD License',
                   'Programming Language :: Python',
		   'Topic :: Database',
		   'Topic :: Software Development :: Libraries'],
      license='BSD'
)
