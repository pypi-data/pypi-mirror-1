ely.advancedquery Package Readme
================================

Overview
--------

Advanced Query extends the Advanced Query extension to zope's ZCatalog
(http://www.dieter.handshake.de/pyprojects/zope/AdvancedQuery.html)

example buildout::

  [buildout]
  parts =
      plone
      zope2
      productdistros
      instance
      zopepy

  # Add additional egg download sources here. dist.plone.org contains archives
  # of Plone packages.
  find-links =
      http://dist.plone.org
      http://download.zope.org/ppix/
      http://download.zope.org/distribution/
      http://effbot.org/downloads


  # Add additional eggs here
  # elementtree is required by Plone
  eggs =
      elementtree

  # Reference any eggs you are developing here, one per line
  # e.g.: develop = src/my.package
  develop =
      .

  [plone]
  recipe = plone.recipe.plone==3.0.3

  [zope2]
  recipe = plone.recipe.zope2install
  url = ${plone:zope2-url}

  [productdistros]
  recipe = plone.recipe.distros
  urls =
    http://www.dieter.handshake.de/pyprojects/zope/AdvancedQuery.tgz
  nested-packages =
  version-suffix-packages =

  [instance]
  recipe = plone.recipe.zope2instance
  zope2-location = ${zope2:location}
  user = admin:admin
  http-address = 8090
  debug-mode = on
  verbose-security = on

  # If you want Zope to know about any additional eggs, list them here.
  # This should include any development eggs you listed in develop-eggs above,
  # e.g. eggs = ${buildout:eggs} ${plone:eggs} my.package
  eggs =
      ely.advancedquery
      ${buildout:eggs}
      ${plone:eggs}

  # If you want to register ZCML slugs for any packages, list them here.
  # e.g. zcml = my.package my.other.package
  zcml =
      ely.advancedquery

  products =
      ${productdistros:location}
      ${plone:products}

  [zopepy]
  recipe = zc.recipe.egg
  eggs = ${instance:eggs}
  interpreter = zopepy
  extra-paths = ${zope2:location}/lib/python
  scripts = zopepy


To buildout and test from source
--------------------------------

::

  python2.4 bootstrap.py
  ./bin/buildout -N -vvv
  ./bin/instance test -m ely.advancedquery

