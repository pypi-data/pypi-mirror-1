from distutils.core import setup

setup (name='unicodescript',
      version='0.7',
      description='Complements the unicodedata module by allowing lookup of the Script attribute of characters.',
      author='Conrad Irwin',
      author_email='conrad.irwin+py@gmail.com',
      license='Python',
      packages=['unicodescript'],
      package_data={'unicodescript':['*']}
)

