Products.plone_gs README
========================

Overview
--------

This product supplies support for exporting / importing the configuration
of the various Plone tools which currently lack such support.  Ideally,
*all* the code in the product will migrate into the corresponding Plone
products over time.

Caveats
-------

- At the moment, this package is tested with Plone 2.5.5.  Updates to
  support more current versions of Plone may come later.

- See the TODO.txt file for a list of the tools which require GS support,
  and to see which ones have complete / partial / missing support.  The
  baseline profile shipped with this product should at least create the
  tools from the correct classes, even where some or all of the tool
  configuration may not be captured.

- The baseline profile does *not* include a step for dumping / loading
  "content-space" objects:  doing such an operation as part of the "site
  setup" export / import is dangerous.  Rather, sites which want to dump
  and load content should use an application like CMFFolderExport, which
  permits content managers to perform the operation without needing to
  manipulate the site configuration.

- The configuration of the user folder is split out into a separate profile,
  registered for the IPluggableAuthService interface.
