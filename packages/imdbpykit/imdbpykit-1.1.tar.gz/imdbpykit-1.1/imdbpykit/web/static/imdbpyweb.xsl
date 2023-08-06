<?xml version="1.0" ?>
<xsl:stylesheet version="1.0"
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

<xsl:output method="html" encoding="utf-8" />

<xsl:variable name="translations" select="document('imdbpyweb-translations.xml')" />
<xsl:variable name="environment" select="document('cache/.environment.xml')" />
<xsl:variable name="lang" select="$environment/environment/lang/@code" />
<xsl:variable name="locale" select="$translations/messages/locale[lang($lang)]" />

<xsl:template name="gettext">
  <xsl:param name="msgid" />

  <xsl:variable name="msgstr" select="$locale/message[@msgid=$msgid]" />
  <xsl:choose>
    <xsl:when test="$msgstr/*">
      <xsl:copy-of select="$msgstr" />
    </xsl:when>
    <xsl:when test="$msgstr//text()">
      <xsl:value-of select="$msgstr//text()" />
    </xsl:when>
    <xsl:otherwise>
      <xsl:value-of select="$msgid" />
    </xsl:otherwise>
  </xsl:choose>
</xsl:template>

<xsl:template match="/">
  <html>
    <head>
      <xsl:choose>
	<xsl:when test="/movie">
          <title><xsl:value-of select="/*/long-imdb-title" /></title>
	</xsl:when>
	<xsl:when test="/person|/character|/company">
          <title><xsl:value-of select="/*/long-imdb-name" /></title>
	</xsl:when>
	<xsl:otherwise>
	  <title>
	    <xsl:call-template name="gettext">
	      <xsl:with-param name="msgid" select="'default-title'"/>
	    </xsl:call-template>
	  </title>
	</xsl:otherwise>
      </xsl:choose>
      <meta http-equiv="content-type" content="text/html; charset=utf-8" />
      <link rel="stylesheet" type="text/css" href="/static/imdbpyweb.css" />
      <script src="/static/imdbpyweb.js" type="text/javascript"
              language="javascript" defer="defer"></script>
    </head>
    <body>
      <xsl:apply-templates />

      <hr />
      <p style="float: right"><small>
	<xsl:call-template name="gettext">
	  <xsl:with-param name="msgid" select="'imdb-disclaimer'"/>
	</xsl:call-template>
      </small></p>
      <small>
	<xsl:call-template name="gettext">
	  <xsl:with-param name="msgid" select="'powered-by-imdbpy'"/>
	</xsl:call-template>
      </small>
    </body>
  </html>
</xsl:template>

<xsl:template match="form">
  <h1>
    <xsl:call-template name="gettext">
      <xsl:with-param name="msgid" select="'form-header'"/>
    </xsl:call-template>
  </h1>

  <p>
    <xsl:call-template name="gettext">
      <xsl:with-param name="msgid" select="'form-search'"/>
    </xsl:call-template>
  </p>

  <form action="search" method="get" name="ig">
    <select name="kind" onChange="document.ig.q.focus();">
      <option selected="1" value="title">
	<xsl:call-template name="gettext">
	  <xsl:with-param name="msgid" select="'form-search-title'"/>
	</xsl:call-template>
      </option>
      <option value="episode">
	<xsl:call-template name="gettext">
	  <xsl:with-param name="msgid" select="'form-search-episode'"/>
	</xsl:call-template>
      </option>
      <option value="people">
	<xsl:call-template name="gettext">
	  <xsl:with-param name="msgid" select="'form-search-person'"/>
	</xsl:call-template>
      </option>
      <option value="character">
	<xsl:call-template name="gettext">
	  <xsl:with-param name="msgid" select="'form-search-character'"/>
	</xsl:call-template>
      </option>
      <option value="company">
	<xsl:call-template name="gettext">
	  <xsl:with-param name="msgid" select="'form-search-company'"/>
	</xsl:call-template>
      </option>
      <option value="keyword">
	<xsl:call-template name="gettext">
	  <xsl:with-param name="msgid" select="'form-search-keyword'"/>
	</xsl:call-template>
      </option>
    </select>&#160;
    <input type="text" size="20" name="q" />&#160;
    <input type="submit" value="Search" />
  </form>

  <div style="text-align: right">
    <small><a href="clear/">
      <xsl:call-template name="gettext">
	<xsl:with-param name="msgid" select="'clear-cache'"/>
      </xsl:call-template>
    </a></small><br />
    <small><a href="search?kind=topbottom&amp;q=top250">
      <xsl:call-template name="gettext">
	<xsl:with-param name="msgid" select="'top250'"/>
      </xsl:call-template>
    </a></small><br />
    <small><a href="search?kind=topbottom&amp;q=bottom100">
      <xsl:call-template name="gettext">
	<xsl:with-param name="msgid" select="'bottom100'"/>
      </xsl:call-template>
    </a></small>
  </div>
</xsl:template>

<xsl:template match="search">
  <h1>Search results for &quot;<xsl:value-of select="query" />&quot;</h1>

  <b>Found <xsl:value-of select="count(result/item)" /> results for
    &quot;<xsl:value-of select="query" />&quot;.</b>

  <xsl:if test="//kind[1]/text()!='keyword'">
  <ol>
    <xsl:for-each select="result/item">
      <li><a href="{@kind}/{@id}"><xsl:apply-templates /></a></li>
    </xsl:for-each>
  </ol>
  </xsl:if>
  <xsl:if test="//kind[1]/text()='keyword'">
  <ol>
    <xsl:for-each select="result/item">
      <li><a href="search?kind=getkeyword&amp;q={@id}"><xsl:apply-templates /></a></li>
    </xsl:for-each>
  </ol>
  </xsl:if>

  <p>Return to the <a href=".">search page</a>.</p>
</xsl:template>

<!-- template for movie/person/character/company pages -->
<xsl:template match="/movie|/person|/character|/company">
  <p>Return to the <a href="..">search page</a>.</p>

  <!-- only one of the two keys below will be present at any time -->
  <h1>
    <xsl:value-of select="long-imdb-title" />
    <xsl:value-of select="long-imdb-name" />
  </h1>

  <input type="button" value="Expand all items"
         onclick="doAll('visible')" />&#160;
  <input type="button" value="Collapse all items"
         onclick="doAll('hidden')" />
  <br />

  <xsl:apply-templates select="." mode="main" />

  <xsl:apply-templates select="left-out-infoset" mode="open" />

  <p>Return to the <a href="..">search page</a>.</p>
</xsl:template>

<xsl:template match="*" mode="title">
  <b>
    <xsl:choose>
      <xsl:when test="@title">
	<xsl:value-of select="@title" />
      </xsl:when>
      <xsl:otherwise>
	<xsl:value-of select="translate(name(), '-', ' ')" />
      </xsl:otherwise>
    </xsl:choose>
  </b>
</xsl:template>

<!-- templates for all first-level data under movie/person/character/company -->

<!-- open mode -->
<xsl:template match="/movie/*|/person/*|/character/*|/company/*"
              mode="open">
  <xsl:variable name="pos" select="count(preceding-sibling::*)" />
  <br />
  <div>
    <span class="mglass" title=" click to expand/collapse "
	  onclick="disappear('{$pos}')">
      <xsl:apply-templates select="." mode="title" />&#160;
    </span>
    <img id="img{$pos}"
	 class="mglass" width="16" height="16"
	 title=" click to expand/collapse "
	 src="/static/less.png"
	 onclick="disappear('{$pos}')" />
    <span id="{$pos}"
	  class="hideable" style="display: inline; visibility: visible;">:
      <xsl:apply-templates select="." mode="default" />
    </span>
  </div>
</xsl:template>

<!-- closed mode -->
<xsl:template match="/movie/*|/person/*|/character/*|/company/*"
              mode="closed">
  <xsl:variable name="pos" select="count(preceding-sibling::*)" />
  <br />
  <div>
    <span class="mglass" title=" click to expand/collapse "
	  onclick="disappear('{$pos}')">
      <xsl:apply-templates select="." mode="title" />&#160;
    </span>
    <img id="img{$pos}"
	 class="mglass" width="16" height="16"
	 title=" click to expand/collapse "
	 src="/static/more.png"
	 onclick="disappear('{$pos}')" />
    <span id="{$pos}"
	  class="hideable" style="display: none; visibility: hidden;">:
      <xsl:apply-templates select="." mode="default" />
    </span>
  </div>
</xsl:template>

<!-- default mode -->
<xsl:template match="/movie/*|/person/*|/character/*|/company/*"
              mode="default" priority="20">
  <xsl:choose>
    <xsl:when test="not(count(*) > 1)">
      <xsl:apply-templates select="." />
    </xsl:when>
    <xsl:when test="not(count(*) > 15)">
      <div class="indent">
	<xsl:for-each select="*">
	  -&#160;<xsl:apply-templates select="." /><br />
	</xsl:for-each>
      </div>
    </xsl:when>
    <xsl:when test="count(*) > 15">
      <xsl:variable name="pos" select="count(preceding-sibling::*)" />
      <div class="indent">
	&#160;&#160;<span
	  class="morelist" title=" click to show/hide all items "
	  onclick="disappearBlock('fl{$pos}')">show full/short list
	  (<xsl:value-of select="count(*)" /> items)</span><br />
	<xsl:for-each select="*[not(position() > 15)]">
	  -&#160;<xsl:apply-templates select="." /><br />
	</xsl:for-each>
	<div id="fl{$pos}" class="hideable"
	     style="display: none; visibility: hidden;">
	  <xsl:for-each select="*[position() > 15]">
	    -&#160;<xsl:apply-templates select="." /><br />
	  </xsl:for-each>
	</div>
      </div>
    </xsl:when>
  </xsl:choose>
</xsl:template>

<xsl:template match="/movie" mode="main">
  <!-- major data -->
  <xsl:apply-templates select="cover-url" mode="open" />
  <xsl:apply-templates select="director" mode="open" />
  <xsl:apply-templates select="writer" mode="open" />
  <xsl:apply-templates select="genres" mode="open" />
  <xsl:apply-templates select="rating" mode="open" />
  <xsl:apply-templates select="cast" mode="open" />
  <xsl:apply-templates select="runtimes" mode="open" />
  <xsl:apply-templates select="countries" mode="open" />
  <xsl:apply-templates select="languages" mode="open" />
  <xsl:apply-templates select="akas" mode="open" />
  <xsl:apply-templates select="plot" mode="open" />

  <!-- remaining data -->
  <xsl:for-each select="*">
    <xsl:sort select="@infoset" />
    <xsl:variable name="node" select="name()" />
    <xsl:if test="($node!='cover-url') and
                  ($node!='director') and
		  ($node!='writer') and
		  ($node!='genres') and
		  ($node!='rating') and
		  ($node!='cast') and
		  ($node!='runtimes') and
		  ($node!='countries') and
		  ($node!='languages') and
		  ($node!='akas') and
		  ($node!='plot')">
      <xsl:apply-templates select="." mode="closed" />
    </xsl:if>
  </xsl:for-each>
</xsl:template>

<xsl:template match="/person|/character" mode="main">
  <!-- major data -->
  <xsl:apply-templates select="headshot" mode="open" />
  <xsl:apply-templates select="birth-name" mode="open" />
  <xsl:apply-templates select="nick-names" mode="open" />
  <xsl:apply-templates select="akas" mode="open" />
  <xsl:apply-templates select="birth-date" mode="open" />
  <xsl:apply-templates select="death-date" mode="open" />
  <xsl:apply-templates select="height" mode="open" />
  <xsl:apply-templates select="spouse" mode="open" />
  <xsl:apply-templates select="filmography" mode="open" />
  <xsl:apply-templates select="director" mode="open" />
  <xsl:apply-templates select="actor" mode="open" />
  <xsl:apply-templates select="actress" mode="open" />
  <xsl:apply-templates select="writer" mode="open" />
  <xsl:apply-templates select="producer" mode="open" />
  <xsl:apply-templates select="self" mode="open" />
  <xsl:apply-templates select="archive-footage" mode="open" />
  <xsl:apply-templates select="introduction" mode="open" />

  <!-- remaining data -->
  <xsl:for-each select="*">
    <xsl:sort select="@infoset" />
    <xsl:variable name="node" select="name()" />
    <xsl:if test="($node!='headshot') and
                  ($node!='birth-name') and
		  ($node!='nick-names') and
		  ($node!='akas') and
		  ($node!='birth-date') and
		  ($node!='death-date') and
		  ($node!='height') and
		  ($node!='spouse') and
		  ($node!='director') and
		  ($node!='actor') and
		  ($node!='actress') and
		  ($node!='writer') and
		  ($node!='producer') and
		  ($node!='self') and
		  ($node!='archive-footage') and
		  ($node!='introduction') and
		  ($node!='filmography')">
      <xsl:apply-templates select="." mode="closed" />
    </xsl:if>
  </xsl:for-each>
</xsl:template>

<xsl:template match="/company" mode="main">
  <!-- major data -->

  <!-- remaining data -->
  <xsl:for-each select="*">
    <xsl:sort select="@infoset" />
    <xsl:apply-templates select="." mode="closed" />
  </xsl:for-each>
</xsl:template>

<!-- elements to ignore -->

<xsl:template match="canonical-title|canonical-name|
                     long-imdb-title|long-imdb-name|
		     long-imdb-canonical-title|long-imdb-canonical-name"
	      mode="closed" priority="90" />
<xsl:template match="series-title|episode-title|
		     canonical-series-title|canonical-episode-title|
		     long-imdb-episode-title"
	      mode="closed" priority="90" />
<xsl:template match="imdbindex" mode="closed" priority="90" />

<xsl:template match="/movie/kind" mode="closed" priority="90" />
<xsl:template match="/movie/year" mode="closed" priority="90" />
<xsl:template match="/movie/title" mode="closed" priority="90" />
<xsl:template match="/movie/votes" mode="closed" priority="90" />

<xsl:template match="/person/name|/character/name"
              mode="closed" priority="90" />
<xsl:template match="/person/birth-notes|/character/birth-notes|
		     /person/death-notes|/character/death-notes"
	      mode="closed" />

<xsl:template match="/company/name" mode="closed" priority="90" />
<xsl:template match="/company/country" mode="closed" priority="90" />

<!-- inline movie/person/character/company elements -->

<xsl:template match="movie" mode="link">
  <a href="../title/{@id}"><xsl:apply-templates select="title" /></a>
</xsl:template>

<xsl:template match="person" mode="link">
  <a href="../name/{@id}"><xsl:apply-templates select="name" /></a>
</xsl:template>

<xsl:template match="character" mode="link">
  <xsl:choose>
    <xsl:when test="@id and (@id!='')">
      <a href="../character/{@id}"><xsl:apply-templates select="name" /></a>
    </xsl:when>
    <xsl:otherwise>
      <xsl:apply-templates select="name" />
    </xsl:otherwise>
  </xsl:choose>
</xsl:template>

<xsl:template match="company" mode="link">
  <a href="../company/{@id}"><xsl:apply-templates select="name" /></a>
</xsl:template>

<xsl:template match="movie|person|character|company">
  <xsl:apply-templates select="." mode="link" />
  <xsl:if test="current-role">
    ...<xsl:apply-templates select="current-role" />
  </xsl:if>
  <xsl:if test="notes">
    &#160;<xsl:apply-templates select="notes" />
  </xsl:if>

  <xsl:for-each select="*[(name()!='title') and
                          (name()!='name') and
			  (name()!='current-role') and
			  (name()!='notes')]">
    <br />&#160;&#160;&#160;&#160;<xsl:apply-templates select="." />
  </xsl:for-each>
</xsl:template>

<xsl:template match="current-role">
  <xsl:variable name="ord" select="count(preceding-sibling::current-role)" />
  <xsl:if test="$ord > 0"> / </xsl:if>
  <xsl:apply-templates />
</xsl:template>

<xsl:template match="notes">
  &#160;<i><xsl:apply-templates /></i>
</xsl:template>

<!-- first-level elements that need special styling -->

<xsl:template match="cover-url">
  <img src="/static/cache/{translate(substring-after(text(), '/images/'), '/', '_')}"
       alt="{../title}" title="{../title}" border="0" />
</xsl:template>

<xsl:template match="headshot">
  <img src="/static/cache/{translate(substring-after(text(), '/images/'), '/', '_')}"
       alt="{../name}" title="{../name}" border="0" />
</xsl:template>

<xsl:template match="birth-date">
  <xsl:apply-templates />
  (<xsl:value-of select="../birth-notes" />)
</xsl:template>

<xsl:template match="death-date">
  <xsl:apply-templates />
  (<xsl:value-of select="../death-notes" />)
</xsl:template>

<xsl:template match="rating">
  <xsl:apply-templates />
  (<xsl:value-of select="../votes" /> votes)
</xsl:template>

<!-- second-level elements that need special styling -->

<xsl:template match="number-of-votes/*">
  <xsl:apply-templates select="." mode="title" />:&#160;
  <xsl:apply-templates /> votes
</xsl:template>

<xsl:template match="demographic/*">
  <xsl:apply-templates select="." mode="title" />:&#160;
  <xsl:apply-templates select="item[2]" />
  (<xsl:apply-templates select="item[1]" /> votes)
</xsl:template>

<xsl:template match="official-sites/*|photo-sites/*|sound-clips/*|video-clips/*|
		     external-reviews/*|newsgroup-reviews/*|misc-links/*">
  <a href="{item[2]}"><xsl:value-of select="item[1]" /></a>
</xsl:template>

<xsl:template match="parents-guide/*|literature/*|connections/*|business/*|
                     recommendations/*|/person/genres/*|/person/keywords/*|
		     /character/quotes/*">
  <xsl:apply-templates select="." mode="title" />
  <xsl:for-each select="*">
    <br />&#160;&#160;&#160;&#160;<xsl:apply-templates select="." />
  </xsl:for-each>
</xsl:template>

<xsl:template match="quote/line">
  <xsl:choose>
    <xsl:when test="count(preceding-sibling::line)>0">
      <div>&#160;&#160;&#160;<xsl:apply-templates /></div>
    </xsl:when>
    <xsl:otherwise>
      <xsl:apply-templates />
    </xsl:otherwise>
  </xsl:choose>
</xsl:template>

<xsl:template match="merchandising-links/*">
  <xsl:apply-templates select="." mode="title" />
  <xsl:for-each select="item[link-text]">
    <br />&#160;&#160;&#160;&#160;<a href="./link"><xsl:value-of select="./link-text" /></a>
  </xsl:for-each>
</xsl:template>

<xsl:template match="awards/*|dvd/*|soundtrack/item/*|amazon-reviews/*|airing/*">
  <b><xsl:value-of select="title|@title|episode" /></b>
  <xsl:for-each select="*[(name()!='title') and (name()!='episode')]">
    <br />&#160;&#160;&#160;&#160;<xsl:apply-templates select="." mode="title" />:&#160;
    <xsl:apply-templates />
  </xsl:for-each>
</xsl:template>

<xsl:template match="news/*">
  <b><a href="{@link}"><xsl:value-of select="title" /></a></b><br />
  &#160;&#160;&#160;&#160;<b>from</b>:
    <a href="{@full-article-link}"><xsl:value-of select="from" /></a>
      (<xsl:value-of select="date" />)<br />
  &#160;&#160;&#160;&#160;<xsl:value-of select="body" />
</xsl:template>

<xsl:template match="episodes/season">
  <b>Season <xsl:value-of select="@number" /></b>
  <xsl:apply-templates />
</xsl:template>

<xsl:template match="season/episode">
  <br />&#160;&#160;<b>#<xsl:value-of select="@number" /></b>: &#160;
  <xsl:apply-templates />
</xsl:template>

<!-- left-out infosets, no "show full/short list" link -->
<xsl:template match="left-out-infoset" mode="closed" priority="90" />
<xsl:template match="left-out-infoset" mode="default" priority="90">
  <div class="indent">
    <xsl:for-each select="*">
      -&#160;<xsl:apply-templates select="." /><br />
    </xsl:for-each>
  </div>
</xsl:template>

<xsl:template match="infoset">
  <a href="../update/{@kind}/{@id}/{@info}">
    <xsl:value-of select="@info" />
  </a>
</xsl:template>

</xsl:stylesheet>
