#!/bin/bash
ID="openplans"

if (( $# == 1 ))
then
	ID="$1"
fi

wget -O /dev/null "http://<<zope_user>>:<<zope_password>>@127.0.0.1:<<zope_port>>/add-openplans.html?form.id=${ID}&form.title=OpenPlans&form.testcontent=&form.actions.add=Add"
