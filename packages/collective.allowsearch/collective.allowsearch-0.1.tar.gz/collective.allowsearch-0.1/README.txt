collective.allowsearch Package Readme
=====================================

Overview
--------

Provides an interface and a default adapter to allow users to search the
catalog independent of the View permission.

Installation
------------

Add this package to your buildout or policy package, or add a ZCML slug
for it to your etc/site.zcml.

Usage
-----

Simply mark any content which you want to be visible in searches for anonymous
users with the IAllowAnonymousSearchMarker interface.

This can be done programmatically or using ZCML like::

    <configure
        xmlns="http://namespaces.zope.org/zope"
        xmlns:five="http://namespaces.zope.org/five"
        i18n_domain="collective.allowsearch">

        <include package="collective.allowsearch" />

        <!--
        EXAMPLE: Allow all ATDocument objects to be found by Anonymous users.
        NOTE: This does _NOT_ change the View permissions in any way.
        -->
        <five:implements
            class="Products.ATContentTypes.content.document.ATDocument"
            interface=".interfaces.IAllowAnonymousSearchMarker"
            />

    </configure>

That's it. See the package's doctest for more information.
