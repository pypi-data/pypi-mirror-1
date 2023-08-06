
collective.recipe.lasso
=======================

This is a buildout recipe for installing lasso_, a C library for single
sign-on, with Python bindings, in a buildout environment.  Lasso supports
SAML 2.0, along with other single sign-on methods.

.. _lasso: http://lasso.entrouvert.org/

Here is an example of how to use this recipe.  The example includes
recipes for building the libxml2, libxslt, and xmlsec dependencies::

    [buildout]
    parts =
        libxml2
        libxslt
        xmlsec
        lasso

    [libxml2]
    recipe = zc.recipe.cmmi
    url = ftp://xmlsoft.org/XSLT/libxml2-2.7.6.tar.gz
    md5sum = 7740a8ec23878a2f50120e1faa2730f2
    extra_options = --without-python

    [libxslt]
    recipe = zc.recipe.cmmi
    url = ftp://xmlsoft.org/XSLT/libxslt-1.1.26.tar.gz
    md5sum = e61d0364a30146aaa3001296f853b2b9
    extra_options = --with-libxml-prefix=${libxml2:location}
                    --without-python

    [xmlsec]
    recipe = zc.recipe.cmmi
    url = http://www.aleksey.com/xmlsec/download/xmlsec1-1.2.13.tar.gz
    md5sum = f8eb1ac14917f47bc35c265c9d76aaab
    # --disable-crypto-dl causes xmlsec to use standard library
    # resolution mechanisms rather than its own fragile method.
    extra_options = --with-libxml=${libxml2:location}
                    --with-libxslt=${libxslt:location}
                    --disable-crypto-dl

    [lasso]
    recipe = collective.recipe.lasso
    # see http://labs.libre-entreprise.org/frs/?group_id=31
    url = http://labs.libre-entreprise.org/frs/download.php/673/lasso-2.2.1.tar.gz
    md5sum = 6548bdb9e334ec075014e68d954948dd
    extra_options =
        --with-python=${buildout:executable}
        --with-pkg-config=${libxml2:location}/lib/pkgconfig:${libxslt:location}/lib/pkgconfig:${xmlsec:location}/lib/pkgconfig
        --disable-java
        --disable-php4
        --disable-php5
        --disable-perl
        --disable-gtk-doc

This recipe is derived from ``zc.recipe.cmmi``.  In addition to what
``zc.recipe.cmmi`` does, this recipe installs the Lasso Python binding
as a fake egg.
