sc.social.viewcounter
=====================

Overview
--------

sc.social.viewcounter provides most accessed / viewed content ranking for Plone 
sites.

Requirements
------------

    * SQLAlchemy 0.5
    
    * z3c.saconfig
    
    * pysqlite (used for testing)
    
    * A database connector 
    
Installation
------------

First step prior to using sc.social.viewcounter is to add a zcml slug to provide a named session 'sc.social.viewcounter.db'. This could be done on the configure.zcml, but you must add the xmlns for db in the configure tag and also include z3c.saconfig into your product ::


    <configure
        ...
        xmlns:db="http://namespaces.zope.org/db"
        ...>
    
        <include package="z3c.saconfig" file="meta.zcml"/>
    
        <db:engine name="sc.social.viewcounter.sqlmemory" url="sqlite:///:memory:" echo="True" />
        <db:session name="sc.social.viewcounter.db" engine="sc.social.viewcounter.sqlmemory" />

    </configure>


Please refer to z3c.saconfig documentation on how to configure url connection strings for your databases.

To enable this product, on a buildout based installation:

    1. Edit your buildout.cfg and add ``sc.social.viewcounter``
       to the list of eggs to install ::

        [buildout]
        ...
        eggs = 
            ...
            sc.social.viewcounter

    2. Tell the plone.recipe.zope2instance recipe to install a ZCML slug::

        [instance]
        ...
        zcml = 
            ...
            sc.social.viewcounter

If another package depends on the sc.social.viewcounter egg or 
includes its zcml directly you do not need to specify anything in the 
buildout configuration: buildout will detect this automatically.

After updating the configuration you need to run the ''bin/buildout'',
which will take care of updating your system.

Go to the 'Site Setup' page in the Plone interface and click on the
'Add/Remove Products' link.

Choose the product (check its checkbox) and click the 'Install' button.

Uninstall -- This can be done from the same management screen, but only
if you installed it from the quick installer.

Note: You may have to empty your browser cache and save your resource registries
in order to see the effects of the product installation.

Sponsoring
----------

Development of this product was sponsored by `Simples Consultoria 
<http://www.simplesconsultoria.com.br/>`_ customers, including (but not limited 
to):

    * `Rede Brasil Atual <http://www.redebrasilatual.com.br/>`_
    
    * `Consumidor Moderno <http://consumidormoderno.uol.com.br/>`_

    * `Ciência Hoje <http://cienciahoje.uol.com.br/>`_

Credits
-------

    * Erico Andrei (erico at simplesconsultoria dot com dot br) - Packaging and
      plumbing.
    
    * Luciano Pacheco (pacheco at simplesconsultoria dot com dot br) - Coding 
      bugfixing and much of day to day use.
      
    * Daniel Vainsencher (daniel at simplesconsultoria dot com dot br) - 
      Bugfixing.

