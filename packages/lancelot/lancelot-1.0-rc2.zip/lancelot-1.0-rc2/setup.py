''' 
distutils setup script.
Will be upgraded to setuptools when that becomes available for python3.
'''

from distutils.core import setup

setup(name='lancelot', 
      version='1.0-rc2',
      packages=['lancelot', 'lancelot.specs', 'lancelot.examples'],
      data_files=[('', ['README.txt', 'COPYING', 'COPYING.LESSER'])],
      provides=['lancelot'],
      license='GNU Lesser General Public License v3 (LGPL v3)',
      description='A behaviour-driven specification and verification library',
      long_description='''lancelot allows class and function behaviour to
be specified and verified using a DSL-like syntax, e.g.::
    @verifiable
    def can_peek_and_pop_after_push():
        spec = Spec(Stack, given=new_stack)
        spec.when(spec.push(value='a'))
        spec.then(spec.peek()).should_be('a')
        spec.then(spec.pop()).should_be('a')
        spec.then(spec.peek()).should_raise(IndexError)
        spec.then(spec.pop()).should_raise(IndexError)
''',
      platforms = ["Windows", "Linux", "Solaris", "Mac OS-X", "Unix"],
      classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Build Tools',
        'Topic :: Software Development :: Documentation',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Software Development :: Quality Assurance',
        'Topic :: Software Development :: Testing',
        'Topic :: Utilities'],
      author='tim bacon',
      author_email='timbacon at gmail dotcom',
      url='http://withaherring.blogspot.com/',
#Development Status :: 5 - Production/Stable
#Development Status :: 6 - Mature
      )
