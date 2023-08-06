=======
Example
=======

    >>> write('buildout.cfg',
    ... """
    ... [buildout]
    ... parts = libsvm
    ...
    ... [libsvm]
    ... recipe = collective.recipe.libsvm
    ... """)

If we run the buildout it returns::

    >>> print system(buildout)
    Installing libsvm.
    libsvm: Downloading ...
    libsvm: Unpacking tarball
    libsvm: Compile svm
    ...
    libsvm: Creating libsvm egg
    <BLANKLINE>

    >>> ls(sample_buildout, 'parts')
    d  libsvm

    >>> ls(sample_buildout, 'eggs')
    -  setuptools-0.6c9-py2.4.egg
    -  svm.egg-link
    d  zc.buildout-1.1.1-py2.4.egg

    >>> print system(buildout)
    Updating libsvm.
    <BLANKLINE>

