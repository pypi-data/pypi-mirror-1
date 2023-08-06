
# pylint: disable-msg=C0103
'''

cli.py
======

Command-line tool for creating FOAF and homepages for Gentoo Linux Developers

Author: Rob Cakebread <pythonhead@gentoo.org>

License : GPL-2

'''

__docformat__ = 'epytext'
__revision__ = '$Revision:  $'[11:-1].strip()


import sha
import sys
import logging
import optparse
from cStringIO import StringIO

from lxml import etree
from rdflib.Graph import ConjunctiveGraph as CGraph
from rdflib import Namespace, Literal, RDF, URIRef

from ternate.utils import COLOR
from ternate.__init__ import __version__ as VERSION

FOAF = Namespace('http://xmlns.com/foaf/0.1/')
RDFS = Namespace('http://www.w3.org/2000/01/rdf-schema#')
DOAP = Namespace('http://usefulinc.com/ns/doap#')
GENTOO = Namespace('http://www.gentoo.org/ns/gentoo#')
HERD = Namespace('http://www.gentoo.org/ns/herd#')

def create_foaf_file(ldap, friends=[]):
    '''Serialize FOAF'''
    graph = CGraph()
    #Make some nice looking namespaces so rdflib doesn't use numbers
    #in the serialization (3_: etc.)
    graph.bind('foaf', FOAF)
    graph.bind('rdfs', RDFS)
    graph.bind('doap', DOAP)
    graph.bind('herd', HERD)
    graph.bind('gentoo', GENTOO)
    
    person = add_foaf_node(graph, ldap)

    #We'll add an option to add friends on the command-line by their
    #developer nick
    for friend in friends:
        knows = add_foaf_node(graph, FOAF, friend)
        ## add the seeAlso link
        graph.add((knows, RDFS['seeAlso'], URIRef(friend.get_foaf_url())))
        graph.add((person, FOAF['knows'], knows))

    return graph.serialize(format="pretty-xml")

def add_foaf_node(graph, ldap):
    '''
    Create a BNode for a Person

    TODO: Create mbox_sha1sum checksum from devname@gentoo.org
          Is there a birthday on Gentoo's LDAP?
    '''
    nick = ldap['uid']
    mbox = sha.new()
    mbox.update('mailto:%s' % ldap['mail'])
    #node = BNode()
    node = URIRef("me")
    # add the ldap data
    graph.add((node, RDF.type, FOAF['Person'] ))
    graph.add((node, FOAF['nick'], Literal(nick)))
    graph.add((node, FOAF['name'], Literal(ldap['cn'])))
    graph.add((node, GENTOO['gentooJoin'], Literal(ldap['gentooJoin'])))
    graph.add((node, FOAF['homepage'],
        URIRef('http://dev.gentoo.org/~%s' % nick)))
    graph.add((node, FOAF['mbox_sha1sum'], Literal(mbox.hexdigest())))
    #This is private LDAP, maybe it's available via passwd. Should add option.
    #graph.add((node, FOAF['dateOfBirth'], Literal(ldap['birthday'])))
    return node

def get_ldap_info(ldap_file):
    '''
    Parses the output of perl_ldap and creates a dictionary with the info
    we want to use in FOAF
    
    '''
    fields = ['uid', 'cn', 'gentooLocation', 'gentooRoles', 'lat', 'lon',
            'gentooJoin', 'mail', 'gpgkey', 'gentooStatus']

    ldap = open(ldap_file).readlines()
    ldap_dict = {}

    for line in ldap:
        if ':' in line:
            key, value = line.split(':')
            key = key.strip()
            if key in fields:
                ldap_dict[key] = value.strip()
    return ldap_dict

def ldap_to_foaf(ldap_file):
    '''
    Get a dictionary of developer LDAP metadata and return a FOAF rendering
    '''
    ldap = get_ldap_info(ldap_file)
    return create_foaf_file(ldap)

def foaf_to_guidexml(foaf_path):
    '''
    Run an XSLT transform of foaf.rdf with developer.xsl stylesheet and get
    nice Gentoo GuideXML output
    '''
    transform = etree.XSLT(etree.fromstring(FOAF_XSL))
    doc = etree.parse(open(foaf_path, 'r'))
    result_tree = transform(doc)
    out = StringIO()
    out.write("")
    result_tree.write(out)
    return out.getvalue()


class Ternate(object):

    '''`Ternate` class'''

    def __init__(self):
        '''Initialize attributes, set logger'''
        self.options = None
        self.log = logging.getLogger('ternate')
        self.log.addHandler(logging.StreamHandler())

    def set_log_level(self):
        '''Set log level according to command-line options'''
        if self.options.verbose:
            self.log.setLevel(logging.INFO)
        elif self.options.quiet:
            self.log.setLevel(logging.ERROR)
        #elif self.options.debug:
        #    self.log.setLevel(logging.DEBUG)
        else:
            self.log.setLevel(logging.WARN)

    def run(self):
        '''
        Run ternate command specified on command-line

        @rtype: int 
        @returns: 0 success or 1 failure
        
        '''
        opt_parser = self.setup_opt_parser()
        (self.options, remaining_args) = opt_parser.parse_args()
        if remaining_args:
            opt_parser.print_help()
            return 1
        self.set_log_level()

        if self.options.ternate_version:
            return ternate_version()

        if self.options.no_color:
            for this in COLOR:
                COLOR[this] = '\x1b[0m'
        if self.options.foaf:
            print ldap_to_foaf(self.options.foaf)
            return

        elif self.options.guidexml:
            print foaf_to_guidexml(self.options.guidexml)
            return
        else:
            opt_parser.print_help()
        return 1

    def setup_opt_parser(self):
        '''
        Setup the optparser

        @rtype: opt_parser.OptionParser
        @return: Option parser

        '''
        usage = 'usage: %prog [options]'
        opt_parser = optparse.OptionParser(usage=usage)

        opt_parser.add_option('--version', action='store_true',
                dest='ternate_version', default=False,
                help='Show ternate version and exit.')

        opt_parser.add_option('-p', '--http-proxy', action='store',
                dest='proxy', default=False,
                help='Specify http proxy URL if you use one.')

        opt_parser.add_option('-l', '--ldap', action='store',
                dest='ldap', default=False,
                metavar='username',
                help='Fetch LDAP info for <username>')

        opt_parser.add_option('-f', '--foaf', action='store',
                dest='foaf', default=False,
                metavar='LDAP file',
                help='Create FOAF from LDAP info')

        opt_parser.add_option('-g', '--guidexml', action='store',
                dest='guidexml', default=False,
                metavar='FOAF file',
                help='Create GuideXML from LDAP info')

        opt_parser.add_option('-C', '--no-color', action='store_true',
                dest='no_color', default=False,
                help="Don't use color in output")

        opt_parser.add_option('-q', '--quiet', action='store_true',
                dest='quiet', default=False, help="Show less output")

        opt_parser.add_option('-v', '--verbose', action='store_true',
                dest='verbose', default=False, help="Show more output")

        return opt_parser


def ternate_version():
    '''Print ternate version'''
    print VERSION


def main():
    '''Let's do it.'''
    my_ternate = Ternate()
    return my_ternate.run()


if __name__ == '__main__':
    sys.exit(main())


FOAF_XSL = '''<?xml version="1.0"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:doap="http://usefulinc.com/ns/doap#" xmlns:herd="http://www.gentoo.org/ns/herd#" xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" xmlns:rdfs="http://www.w3.org/2000/01/rdf-schema#" xmlns:foaf="http://xmlns.com/foaf/0.1/" xmlns:dc="http://purl.org/dc/elements/1.1/" version="1.0" xml:lang="en" xmlns:air="http://www.megginson.com/exp/ns/airports#" xmlns:wn="http://xmlns.com/wordnet/1.6/" xmlns:contact="http://www.w3.org/2000/10/swap/pim/contact#" xmlns:geo="http://www.w3.org/2003/01/geo/wgs84_pos#">
  <xsl:output method="xml" version="1.0" encoding="UTF-8" indent="yes"/>
  <xsl:key name="indi" match="foaf:Person" use="@rdf:about"/>
  <xsl:template match="/">
    <guide link="/developer.xml">
      <title>
        <xsl:value-of select="/rdf:RDF/foaf:Person[@rdf:about='me']/foaf:name"/>
      </title>
      <author title="Author">
        <xsl:element name="mail">
          <xsl:attribute name="link">
            <xsl:value-of select="/rdf:RDF/foaf:Person[@rdf:about='me']/foaf:nick"/>
          </xsl:attribute>
        </xsl:element>
      </author>
      <abstract>
This is the developer homepage of <xsl:value-of select="/rdf:RDF/foaf:Person[@rdf:about='me']/foaf:nick"/>
</abstract>
      <!-- The content of this document is licensed under the CC-BY-SA license -->
      <!-- See http://creativecommons.org/licenses/by-sa/2.5 -->
      <license/>
      <version>0.1</version>
      <date>2008-06-27</date>
      <chapter>
        <title>Developer Info</title>
        <section>
          <title>Vitals</title>
          <body>
            <xsl:for-each select="rdf:RDF/foaf:Person[@rdf:about='me']">
              <xsl:element name="a">
                <xsl:attribute name="name">
                  <xsl:value-of select="@rdf:about='me'"/>
                </xsl:attribute>
              </xsl:element>
                <dl>
                    <!-- We're in trouble if they add another nick since we want to do stuff with the Gentoo developer nick. So we should make a 'holdsAccount' and use the username from it -->
                  <dt>Nick: </dt>
                  <dd>
                    <xsl:value-of select="foaf:nick"/>
                  </dd>
                  <xsl:if test="foaf:gender">
                  <dt>Gender: </dt>
                  <dd>
                    <xsl:value-of select="foaf:gender"/>
                  </dd>
                  </xsl:if>
                  <dt>Mailbox sha1sum : </dt>
                  <xsl:for-each select="foaf:mbox_sha1sum">
                    <dd>
                      <xsl:value-of select="."/>
                    </dd>
                  </xsl:for-each>
                  <dt>Homepage : </dt>
                  <xsl:for-each select="foaf:homepage">
                    <dd>
                      <xsl:element name="uri">
                        <xsl:value-of select="@rdf:resource"/>
                      </xsl:element>
                    </dd>
                  </xsl:for-each>
                  <xsl:if test="foaf:weblog">
                  <dt>Blog : </dt>
                  <xsl:for-each select="foaf:weblog">
                    <dd>
                      <xsl:element name="uri">
                        <xsl:value-of select="@rdf:resource"/>
                      </xsl:element>
                    </dd>
                  </xsl:for-each>
                  </xsl:if>
                  <xsl:if test="foaf:based_near">
                  <dt>Location : </dt>
                  <xsl:for-each select="foaf:based_near/geo:Point">
                  <dd>
                      <xsl:text>Lattitude </xsl:text><xsl:value-of select="geo:lat"/>
                      </dd>
                  <dd>
                      <xsl:text>Longitude </xsl:text><xsl:value-of select="geo:long"/>
                      </dd>

                  </xsl:for-each>
                  </xsl:if>

                  <xsl:if test="foaf:openid">
                  <dt>OpenID : </dt>
                  <xsl:for-each select="foaf:openid">
                    <dd>
                      <xsl:element name="uri">
                        <xsl:value-of select="@rdf:resource"/>
                      </xsl:element>
                    </dd>
                  </xsl:for-each>
                  </xsl:if>
                  <xsl:if test="foaf:currentProject/herd:Project">
                  <dt>Herds : </dt>
                  <dd>
                    <xsl:for-each select="foaf:currentProject/herd:Project">
                      <xsl:apply-templates select="."/>
                    </xsl:for-each>
                </dd>
                  </xsl:if>

                  <xsl:if test="foaf:currentProject/doap:Project">
                  <dt>Other OSS Projects : </dt>
                    <xsl:for-each select="foaf:currentProject/doap:Project">
                  <dd>
                            <xsl:element name="uri">
                                <xsl:attribute name="link"><xsl:value-of select="doap:homepage/@rdf:resource"/></xsl:attribute>
                                <xsl:apply-templates select="."/>
                            </xsl:element>
                </dd>
                    </xsl:for-each>
                  </xsl:if>
                  <dt>Stats : </dt>
                  <dd>
                      <xsl:element name="uri">
                        <xsl:attribute name="link">
                      http://cia.navi.cx/stats/author/<xsl:value-of select="/rdf:RDF/foaf:Person/foaf:nick"/>
                        </xsl:attribute>
                        Commits
                      </xsl:element>
                  </dd>

                  <dd>
                      <xsl:element name="uri">
                          <xsl:attribute name="link">
                              <xsl:text>http://bugs.gentoo.org/buglist.cgi?bug_status=NEW;bug_status=ASSIGNED;bug_status=REOPENED;email1=</xsl:text><xsl:value-of select="/rdf:RDF/foaf:Person/foaf:nick"/><xsl:text>%40gentoo.org;emailtype1=exact;emailassigned_to1=1;emailreporter1=1</xsl:text></xsl:attribute>
                          <xsl:text>Bugs</xsl:text>
                      </xsl:element>
                  </dd>

                  <xsl:if test="foaf:JabberID">
                  <dt>Jabber Id : </dt>
                  <xsl:for-each select="foaf:jabberID">
                    <dd>
                      <xsl:value-of select="."/>
                    </dd>
                  </xsl:for-each>
                  </xsl:if>

                  <xsl:if test="foaf:holdsAccount">
                  <dt>Misc Accounts : </dt>
                  <xsl:for-each select="foaf:holdsAccount/foaf:OnlineAccount">
                    <dd>
                        <xsl:choose>
                          <xsl:when test="@rdf:about">
                            <xsl:element name="uri">
                              <xsl:attribute name="link"><xsl:value-of select="@rdf:about"/></xsl:attribute>
                              <xsl:value-of select="foaf:accountName"/>
                              <xsl:text> - </xsl:text>
                              <xsl:value-of select="foaf:accountServiceHomepage/@rdf:resource"/>
                            </xsl:element>
                          </xsl:when>
                          <xsl:otherwise>
                            <xsl:value-of select="foaf:accountName"/>
                            <xsl:text> - </xsl:text>
                            <xsl:element name="uri">
                              <xsl:attribute name="link"><xsl:value-of select="foaf:accountProfilePage/@rdf:resource"/></xsl:attribute>
                              <xsl:value-of select="foaf:accountProfilePage/@rdf:resource"/>
                            </xsl:element>
                          </xsl:otherwise>
                        </xsl:choose>
          </dd>
                  </xsl:for-each>

                  </xsl:if>
                  <xsl:for-each select="foaf:depiction">
                    <dt>Photos : </dt>
                    <dd>
                      <xsl:element name="img">
                        <xsl:attribute name="src">
                          <xsl:value-of select="@rdf:resource"/>
                        </xsl:attribute>
                        <xsl:value-of select="@rdf:resource"/>
                      </xsl:element>
                    </dd>
                  </xsl:for-each>
                </dl>
            </xsl:for-each>
          </body>
        </section>
      </chapter>
    </guide>
  </xsl:template>
</xsl:stylesheet>
'''
