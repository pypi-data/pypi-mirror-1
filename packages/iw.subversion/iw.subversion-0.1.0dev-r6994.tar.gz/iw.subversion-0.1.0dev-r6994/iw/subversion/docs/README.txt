================
iw.subversion package
================

.. contents::

What is iw.subversion ?
=======================

This package contains helpers for SVN integration.

How to use iw.subversion ?
==========================

`iw.subversion` provides a `svn_check_source` console script. 
This script has to be called in the pre-commit hook script 
(look up in SVN documentation). The call should look like::

    svn_check_source "$REPOS" "$TXN" || exit 1

