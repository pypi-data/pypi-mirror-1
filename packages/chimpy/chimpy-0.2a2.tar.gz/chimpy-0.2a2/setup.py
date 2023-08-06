from setuptools import setup, find_packages

readme = open("chimpy/README.txt").read()

setup(name='chimpy',
      version='0.2a2',
      description='Python wrapper for the MailChimp API',
      long_description=readme,
      classifiers = [
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
      ],
      keywords = 'email mail mailinglist newsletter',
      author='James Casbon, Anton Stonor',
      author_email='casbon@gmail.com',
      url = 'http://code.google.com/p/chimpy/',
      license = 'New BSD License',
      packages=find_packages(),
      zip_safe=False,
      install_requires=[
        'simplejson', ]
      )
