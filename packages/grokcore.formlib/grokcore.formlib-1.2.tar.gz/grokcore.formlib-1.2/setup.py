from setuptools import setup, find_packages
import os

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

long_description = (
    read('README.txt')
    + '\n' +
    read('CHANGES.txt')
    )

setup(
    name='grokcore.formlib',
    version = '1.2',
    author='Grok Team',
    author_email='grok-dev@zope.org',
    url='http://grok.zope.org',
    download_url='http://cheeseshop.python.org/pypi/grokcore.formlib',
    description='Grok-like configuration for zope.formlib components',
    long_description=long_description,
    license='ZPL',
    classifiers=['Environment :: Web Environment',
                 'Intended Audience :: Developers',
                 'License :: OSI Approved :: Zope Public License',
                 'Programming Language :: Python',
                 'Framework :: Zope3',
                 ],

    packages=find_packages('src'),
    package_dir = {'': 'src'},
    namespace_packages=['grokcore'],
    include_package_data = True,
    zip_safe=False,
    install_requires=['setuptools',
                      'martian >= 0.10',
                      'grokcore.component >= 1.5',
                      'grokcore.security >= 1.1',
                      'grokcore.view >= 1.9',
                      'zope.formlib',
                      # for tests:
                      'zope.testing',
                      'zope.lifecycleevent',
                      'zope.securitypolicy',
                      'zope.app.zcmlfiles',
                      ],
)
