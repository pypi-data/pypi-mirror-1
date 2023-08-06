try:
    from setuptools import setup
    setup_kwargs = {'zip_safe': False}
except ImportError:
    from distutils.core import setup
    setup_kwargs = {}
    

setup(
    name='django-freeperms',
    version='0.1',
    license='BSD',

    keywords='django middleware permissions auth',
    description="Django middleware for enabling anonymous permissions",
    url='http://pypi.python.org/pypi/django-freeperms',

    author='Tamas Kemenczy',
    author_email='tamas.kemenczy@gmail.com',

    classifiers=(
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ),

    packages=(
        'freeperms',
    ),

    **setup_kwargs
)
