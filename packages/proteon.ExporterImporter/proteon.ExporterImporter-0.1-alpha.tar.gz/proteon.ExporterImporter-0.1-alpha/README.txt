- Code repository: https://svn.plone.org/svn/collective/proteon.ExporterImporter
- Questions and comments to hduran "at" machinalis [dot] com
- Report bugs by mail for now

-- INSTALL

Add proteon.exporterimporter to the list of eggs to install, e.g.:

    [buildout]
    ...
    eggs =
       ...
       products.ExporterImporter

With portal_quickinstaller install Proteon SQL Importer

-- USAGE

 - put the results of exports (untared) on $INSTANCE/var/sql_exporter
 - from @@manage_massive_exportimporter set where to start the import, save, and start importing

