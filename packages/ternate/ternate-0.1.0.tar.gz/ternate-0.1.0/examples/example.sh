#!/bin/bash

ssh $1@dev.gentoo.org  '/usr/local/bin/perl_ldap -b anon -s $1' > ldap.txt
/usr/bin/ternate --foaf ldap.txt foaf.rdf
/usr/bin/ternate --guidexml foaf.rdf index.xml
/usr/bin/gorg < index.xml > index.html
