try:
    from setuptools import setup, find_packages
    packages = find_packages()
    extra_kwds = dict(
        install_requires = ['Django>=0.96', 'PIL', 'markdown'])
except ImportError:
    from distutils.core import setup
    import os
    packages = []
    for root, dirs, files in os.walk('.'):
        if '__init__.py' in files:
            # i.e. root='./blogmaker/blog' 
            packages.append(root.replace(os.path.sep, '.')[2:])
    extra_kwds = {}
setup(name='Blogmaker',
      version='0.6',
      description='Blog application for Django',
      author='Peter Bernheim, Kent S Johnson',
      author_email='blogmaker@blogcosm.com',
      url='http://code.google.com/p/blogmaker/',
      license='BSD License',
      keywords='django blog'.split(),
      packages=packages,
      classifiers=[
          'Development Status :: 5 - Production/Stable',
          'Environment :: Web Environment',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: BSD License',
          'Natural Language :: English',
          'Operating System :: OS Independent',
          'Programming Language :: Python',
          'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
          ],
      platforms='any',
      long_description='''Blogmaker is a full-featured, production-quality blogging application for Django.
It supports trackbacks, ping, comments with moderation and 
honeypot spam prevention and many other features.''',
      **extra_kwds
      )
