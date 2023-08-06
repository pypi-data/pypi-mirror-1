from setuptools import setup

kwargs = {
    'name' : 'markuputils',
    'version' : '0.3dev',
    'description' : 'Markup utilities for Django applications.',
    'author' : 'Christos Trochalakis',
    'author_email' : 'yatiohi@ideopolis.gr',
    'url' : 'http://github.com/ctrochalakis/django-markuputils',
    'packages' : ['markup_utils',
                  'markup_utils.templatetags'],
    'classifiers' : ['Development Status :: 4 - Beta',
                     'Environment :: Web Environment',
                     'Intended Audience :: Developers',
                     'License :: OSI Approved :: BSD License',
                     'Operating System :: OS Independent',
                     'Programming Language :: Python',
                     'Framework :: Django',
                     'Topic :: Utilities'],
    'include_package_data' : False,
    'zip_safe' : False,
}

setup(**kwargs)
