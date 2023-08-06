from distutils.core import setup

setup (name='unicodescript',
      version='0.8',
      description='Complements the unicodedata module by allowing lookup of the Script attribute of characters in Unicode 5.2.0.',
      author='Conrad Irwin',
      author_email='conrad.irwin+py@gmail.com',
      license='Python',
      packages=['unicodescript'],
      package_data={'unicodescript':['*']}
)

