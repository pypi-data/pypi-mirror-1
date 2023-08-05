from setuptools import setup, find_packages

name = "plone.recipe.command"
setup(
    name = name,
    version = "1.0",
    author = "Daniel Nouri",
    author_email = "daniel.nouri@gmail.com",
    description = "Execute arbitrary commands in buildout through os.system",
    license = "GPL",
    keywords = "buildout",
    url='http://www.python.org/pypi/'+name,

    packages=find_packages(exclude=['ez_setup']),
    namespace_packages=['plone.recipe'],
    include_package_data=True,
    zip_safe=False,
    install_requires = ['zc.buildout', 'setuptools'],
    entry_points = {'zc.buildout':
                    ['default = %s:Recipe' % name]},
    )
