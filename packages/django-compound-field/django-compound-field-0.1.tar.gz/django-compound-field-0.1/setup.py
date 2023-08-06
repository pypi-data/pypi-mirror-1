from setuptools import setup, find_packages
 
setup(
    name='django-compound-field',
    version="0.1",
    description='A compound field for Django',
    long_description=open('README.rst').read(),
    author='Johannes Dollinger',
    maintainer='Andreas Kostyrka',
    maintainer_email='andreas@kostyrka.org',
    license='BSD',
    packages=find_packages(exclude=['ez_setup']),
    include_package_data=True,
    zip_safe=False,
    install_requires=["nose",
                      "django>=1.1"],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
