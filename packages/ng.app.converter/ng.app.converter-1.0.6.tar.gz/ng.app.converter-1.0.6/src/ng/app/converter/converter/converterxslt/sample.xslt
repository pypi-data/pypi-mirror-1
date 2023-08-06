<xsl:stylesheet
	version="1.0"
	xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

      <!-- This template used to clean up html sources -->

      <xsl:template match="a">
        <xsl:copy>
          <xsl:apply-templates select="node()|attribute::href"/>
        </xsl:copy>
      </xsl:template> 

      <!-- <xsl:template match="img">
        <xsl:copy>
          <xsl:apply-templates select="node()|attribute::src"/>
        </xsl:copy>
      </xsl:template> -->

     <xsl:template match="meta">
        <xsl:copy>
          <xsl:apply-templates select="node()|attribute::*"/>
        </xsl:copy>
      </xsl:template> 

      <xsl:template match="p|h1|h2|h3|h4|h5|b|i|ul|ol|li|dl|dd|df|th|tr|td|table|body|html"> 
        <xsl:copy> 
          <xsl:apply-templates select="node()"/>
        </xsl:copy>
      </xsl:template>  

      <xsl:template match="img|div|span"> 
          <xsl:apply-templates select="node()"/>
      </xsl:template> 

      <xsl:template match="form|head|script|link|br|comment()|nobr"> 
	  <xsl:apply-templates select="meta"/>
      </xsl:template> 

      <xsl:template match="@*|node()">
        <xsl:copy> 
          <xsl:apply-templates select="@*|node()"/>
        </xsl:copy>
      </xsl:template> 

</xsl:stylesheet>
