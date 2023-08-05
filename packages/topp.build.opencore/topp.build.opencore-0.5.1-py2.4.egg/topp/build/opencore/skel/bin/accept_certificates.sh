#!/bin/bash

# ensure the certificates are accepted for svn
# svn should really have the --no-certificate option,
# but since it doesn't we'll work around

echo p | svn ls https://svn.plone.org/svn/plone
echo p | svn ls https://svn.openplans.org/svn
