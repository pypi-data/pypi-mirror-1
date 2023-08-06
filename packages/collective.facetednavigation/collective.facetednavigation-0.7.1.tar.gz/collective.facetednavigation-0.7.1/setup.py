import os
import os.path
from setuptools import setup
from setuptools import find_packages

version_file = os.path.join('src', 'collective', 'facetednavigation',
                            'VERSION.txt')
version = open(version_file).read().strip()
description_file = 'README.txt'
description = open(description_file).read().split('\n\n')[0].strip()
description = description.replace('\n', ' ')
long_description_file = os.path.join('src', 'collective', 'facetednavigation',
                                     'README.txt')
long_description = open(long_description_file).read().strip()


setup(
    name='collective.facetednavigation',
    version=version,
    packages=find_packages('src'),
    namespace_packages=['collective', ],
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,

    entry_points={},

    author='Damien Baty',
    author_email='damien.baty@removethis.gmail.com',
    description=description,
    long_description=long_description,
    license='GNU GPL',
    classifiers=['Development Status :: 4 - Beta',
                 'Environment :: Web Environment',
                 'Framework :: Plone',
                 'Intended Audience :: Developers',
                 'Intended Audience :: End Users/Desktop',
                 'Intended Audience :: Information Technology',
                 'License :: OSI Approved :: GNU General Public License (GPL)',
                 'Natural Language :: English',
                 'Natural Language :: French',
                 'Operating System :: OS Independent',
                 'Programming Language :: Python',
                 ],
    keywords='Plone facet faceted navigation user interface',
    url='http://plone.org/products/faceted-navigation',
    download_url='http://cheeseshop.python.org/pypi/collective.facetednavigation',
    )
