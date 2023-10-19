from setuptools import setup, find_packages

setup(
    name='pulumi_vsphere_module',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'pulumi',
        'pulumi_vsphere',
        'jinja2',
    ],
    include_package_data=True,
    author='Your Name',
    author_email='your_email@example.com',
    description='Pulumi vSphere module for creating virtual machines',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/your_username/pulumi_vsphere_module',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)
