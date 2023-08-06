gocept.cxoracle - A zc.buildout recipe to easily get cx_Oracle running

An example buildout might look like this::

    [buildout]
    develop = .
    parts = python-oracle cx_Oracle test
    python = python-oracle

    [python-oracle]
    recipe = gocept.cxoracle
    instant-client = .../instantclient-basiclite-macosx-10.2.0.4.0.zip
    instant-sdk = .../instantclient-sdk-macosx-10.2.0.4.0.zip

    [cx_Oracle]
    recipe = zc.recipe.egg:custom
    egg = cx_Oracle

    [test]
    recipe = zc.recipe.testrunner
    eggs = test.some.egg
