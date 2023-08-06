Introduction
============


This package provides an light-weight API for ``vudo`` packages which provide
user-changeable skins.  These packages may advertise their skin directory using
``setuptools entry points``.

Additionally, this package provides a script to manage the skin directory of a
``vudo`` project in a convenient way.

Usage
=====

Developers, which want to make ``vudo`` packages which provide skins, need to
include their skin resources in the EGG, and include a entry point.

Skin Resources
--------------

Depending whether or not a SCM system supported by setuptools (currently SVN)
is used or not, developers may need to include their resources manually using
``package_data``::

    setup(name='vudo.compositepage',
          ...
          packages=find_packages('src'),
          package_dir = {'': 'src'},
          package_data = {
              "vudo.compositepage": [
                  "skin/*.zcml",
                  "skin/compositepage/*.zcml",
                  "skin/compositepage/ajax/*.pt",
                  "skin/region/*.pt",
                  ]
              },
          ...
          )

Entry Point
-----------

Additionally to include the skin resources in the package egg, the skin needs
to be advertized using a ``entry point``::

    setup(name='vudo.compositepage',
          ...
          entry_points="""
          # -*- Entry points: -*-
          [vudo.skin]
          compositepage=vudo.compositepage:provide_skin [skin]
          """,
          extras_require={
              "skin": "vudo.skinsetup",
          },
          ...
      )

The ``provide_skin`` mentioned above needs to call the ``vudo.skinsetup``
package API to return the skin information::

    def provide_skin():
        import os
        from vudo.skinsetup import provide_skin
        return provide_skin(
                package="vudo.compositepage",
                name="compositepage",
                skin_path="skin")

the parameters to the ``provide_skin`` method are as follows:

package
  The package name which provides the skin

name
  The skin name

skin_path
  The ``path`` to the skin within the package.  Note, this is usually a
  ``setuptools`` resource path, and thus always "/" separated.  Do not use
  ``os.path``.

Links
=====

Pkg resources and Entry Points
  http://peak.telecommunity.com/DevCenter/PkgResources#entry-points
  http://peak.telecommunity.com/DevCenter/PkgResources#resourcemanager-api

Quick tutorial
  http://wiki.pylonshq.com/display/pylonscookbook/Using+Entry+Points+to+Write+Plugins

