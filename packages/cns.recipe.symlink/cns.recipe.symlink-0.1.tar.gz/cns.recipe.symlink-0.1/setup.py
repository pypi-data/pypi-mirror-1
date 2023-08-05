from setuptools import setup, find_packages

name = "cns.recipe.symlink"
setup(
    name = name,
    version = "0.1",
    author = "Radim Novotny",
    author_email = "radim.novotny@corenet.cz",
    description = "Create symlinks",
    long_description="""\
    Simple recipe for creating symbolic links. 

    Parameters:
    
       - *symlink* contains one or more values in format source=target
       - *symlink_base* can contain base directory for symlinking (simplifies *symlink* parameter if there is more items from the same directory)
       - *symlink_target* can contain target base directory(simplifies *symlink* parameter if target is still the same. In this case *symlink* can be in format **source=**)

       Example 1::

         [symlinks]
         symlink = ~/work/MyProj = ${buildout:directory}/products

       Example 2::

         [symlinks]
         symlink = MyProj
                   MyOtherProj
                   MyThirdProj
         symlink_base = ~/work/
         symlink_target = ${buildout:directory}/products
         
       Example 3::

                 [symlinks]
                 symlink = MyProj
                           MyOtherProj
                           ${buildout:directory}/var/fss-files=${instance1:location}/var
                 symlink_base = ~/work/
                 symlink_target = ${buildout:directory}/products
    """,

    license = "GPL",
    keywords = "buildout",
    url='http://corenet-int.com',

    packages=find_packages(exclude=['ez_setup']),
    namespace_packages=['cns.recipe'],
    include_package_data=True,
    zip_safe=False,
    install_requires = ['zc.buildout', 'setuptools'],
    entry_points = {'zc.buildout':
                    ['default = %s:Recipe' % name]},
    )
