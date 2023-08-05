import os
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

long_description = (
    read('README.txt')
    + '\n' +
    read('CHANGES.txt')
    + '\n' +
    'Download\n'
    '========\n'
)
name = "pylons_sandbox"
setup(
    description = """An experimental Buildout recipe backwards-compatible with zc.buildout.egg but with extra features for Pylons users.""",
    author = 'James Gardner',
    author_email = 'james at pythonweb dot org',
    long_description = long_description,
    name = name,
    packages = find_packages(),
    include_package_data = True,
    version = "0.1.0",
    install_requires = ['zc.buildout >=1.0.0b30', 'zc.recipe.egg'],
    entry_points = {'zc.buildout': ['default = %s:Scripts' % name,
                                    'script = %s:Scripts' % name,
                                    'scripts = %s:Scripts' % name,
                                    'eggs = %s:Eggs' % name,
                                    'custom = %s:Custom' % name,
                                    'develop = %s:Develop' % name,
                                    ]
                    },
    classifiers = [
       'Framework :: Buildout',
       'Development Status :: 3 - Alpha',
       'Intended Audience :: Developers',
       'License :: OSI Approved :: Zope Public License',
       'Topic :: Software Development :: Build Tools',
       'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
