<?xml version="1.0"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:doap="http://usefulinc.com/ns/doap#" xmlns:herd="http://www.gentoo.org/ns/herd#" xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" xmlns:rdfs="http://www.w3.org/2000/01/rdf-schema#" xmlns:foaf="http://xmlns.com/foaf/0.1/" xmlns:dc="http://purl.org/dc/elements/1.1/" version="1.0" xml:lang="en" xmlns:air="http://www.megginson.com/exp/ns/airports#" xmlns:wn="http://xmlns.com/wordnet/1.6/" xmlns:contact="http://www.w3.org/2000/10/swap/pim/contact#" xmlns:geo="http://www.w3.org/2003/01/geo/wgs84_pos#">
  <xsl:output method="xml" version="1.0" encoding="UTF-8" indent="yes"/>
  <xsl:key name="indi" match="foaf:Person" use="@rdf:ID"/>
  <xsl:template match="/">
    <guide link="/developer.xml">
      <title>
        <xsl:value-of select="/rdf:RDF/foaf:Person[@rdf:ID='me']/foaf:name"/>
      </title>
      <author title="Author">
        <xsl:element name="mail">
          <xsl:attribute name="link">
            <xsl:value-of select="/rdf:RDF/foaf:Person[@rdf:ID='me']/foaf:nick"/>
          </xsl:attribute>
        </xsl:element>
      </author>
      <abstract>
This is the developer homepage of <xsl:value-of select="/rdf:RDF/foaf:Person[@rdf:ID='me']/foaf:nick"/>
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
            <xsl:for-each select="rdf:RDF/foaf:Person[@rdf:ID='me']">
              <xsl:element name="a">
                <xsl:attribute name="name">
                  <xsl:value-of select="@rdf:ID='me'"/>
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
                  <dt>Blog : </dt>
                  <xsl:for-each select="foaf:weblog">
                    <dd>
                      <xsl:element name="uri">
                        <xsl:value-of select="@rdf:resource"/>
                      </xsl:element>
                    </dd>
                  </xsl:for-each>
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
                  <dt>Herds : </dt>
                  <dd>
                    <xsl:for-each select="foaf:currentProject/herd:Project">
                      <xsl:apply-templates select="."/>
                    </xsl:for-each>
                </dd>

                  <dt>Other OSS Projects : </dt>
                    <xsl:for-each select="foaf:currentProject/doap:Project">
                  <dd>
                            <xsl:element name="uri">
                                <xsl:attribute name="link"><xsl:value-of select="doap:homepage/@rdf:resource"/></xsl:attribute>
                                <xsl:apply-templates select="."/>
                            </xsl:element>
                </dd>
                    </xsl:for-each>

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
