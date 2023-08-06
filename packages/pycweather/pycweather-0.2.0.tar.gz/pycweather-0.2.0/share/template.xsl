<?xml version="1.0" encoding="UTF-8"?>
<!-- pycweather/template.xsl: XSL stylesheet for displaying weather

This file is part of PycWeather

Copyright (c) 2009 Vlad Glagolev <enqlave@gmail.com>. All rights reserved.

Permission to use, copy, modify, and distribute this software for any
purpose with or without fee is hereby granted, provided that the above
copyright notice and this permission notice appear in all copies.

THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

-->
<xsl:stylesheet xmlns="http://www.w3.org/1999/xhtml" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">
	<xsl:output method="text" disable-output-escaping="yes"/>
	<xsl:variable name="nl">
		<xsl:text>&#10;</xsl:text>
	</xsl:variable>
	<xsl:template match="weather">
		<xsl:apply-templates select="cc"/>
		<xsl:apply-templates select="dayf"/>
		<xsl:comment>PycWeather</xsl:comment>
	</xsl:template>
	<xsl:template match="cc">
		<xsl:text>Location: </xsl:text><xsl:value-of select="obst"/><xsl:text> (</xsl:text><xsl:value-of select="../loc/lat"/><xsl:text>, </xsl:text><xsl:value-of select="../loc/lon"/><xsl:text>)</xsl:text><xsl:value-of select="$nl"/>
		<xsl:text>Temperature: </xsl:text><xsl:value-of select="tmp"/>°<xsl:value-of select="../head/ut"/><xsl:value-of select="$nl"/>
		<xsl:if test="tmp != flik">
			<xsl:text>Windchill: </xsl:text><xsl:value-of select="flik"/>°<xsl:value-of select="../head/ut"/><xsl:value-of select="$nl"/>
		</xsl:if>
		<xsl:text>Conditions: </xsl:text><xsl:value-of select="t"/><xsl:value-of select="$nl"/>
		<xsl:text>Wind: </xsl:text>
		<xsl:choose>
			<xsl:when test="wind/s = 'calm'">
				<xsl:text>0</xsl:text>
			</xsl:when>
			<xsl:otherwise>
				<xsl:value-of select="wind/s"/>
			</xsl:otherwise>
		</xsl:choose>
		<xsl:value-of select="../head/us"/>
		<xsl:text> (</xsl:text><xsl:value-of select="wind/t"/><xsl:text>)</xsl:text>
	</xsl:template>
	<!-- MULTIPLE DAYS DISPLAY -->
	<xsl:template match="dayf">
		<!-- don't repeat the first one -->
		<xsl:apply-templates select="child::day[position() > 1]"/>
	</xsl:template>
	<xsl:template match="day">
		<xsl:value-of select="$nl"/>
		<xsl:value-of select="@dt"/><xsl:text>, </xsl:text><xsl:value-of select="@t"/>
		<xsl:if test="@d = 1">
			<xsl:text> (Tomorrow)</xsl:text>
		</xsl:if>
		<xsl:text>: </xsl:text>
		<xsl:apply-templates select="part"/>
	</xsl:template>
	<xsl:template match="part">
		<xsl:choose>
			<xsl:when test="@p = 'd'">
				<xsl:text>Day (</xsl:text>
				<xsl:value-of select="../hi"/>°<xsl:value-of select="../../../head/ut"/>
			</xsl:when>
			<xsl:otherwise>
				<xsl:text>Night (</xsl:text>
				<xsl:value-of select="../low"/>°<xsl:value-of select="../../../head/ut"/>
			</xsl:otherwise>
		</xsl:choose>
		<xsl:text>, </xsl:text>
		<xsl:apply-templates select="t"/>
		<xsl:text>)</xsl:text>
		<xsl:if test="@p = 'd'">
			<xsl:text>; </xsl:text>
		</xsl:if>
	</xsl:template>
</xsl:stylesheet>
