from setuptools import setup, find_packages

setup(
    name='django_excel_templates',
    version='0.1',
    description='Generate Excel Tables from Django',
    long_description=open("README.txt").read(),
    author='bray, dean.sellis, tkemenczy, chalkdust1011, et al',
    author_email='bray@sent.com',
    url='http://code.google.com/p/django-excel-templates/',
    packages=find_packages(exclude=['test']),
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Framework :: Django',
    ],
    include_package_data=True,
    install_requires=[
        'xlwt' 
    ],
    zip_safe=True,
)
