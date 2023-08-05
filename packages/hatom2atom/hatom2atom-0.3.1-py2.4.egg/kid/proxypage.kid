<?xml version='1.0' encoding='utf-8'?>
<html xmlns="http://www.w3.org/1999/xhtml"
      xmlns:py="http://purl.org/kid/ns#"
>
<!--
proxy_page - kid template for hatom2atom proxy

this file is part of the hatom2atom package.

created and maintained by luke arno <luke.arno@gmail.com>

copyright (c) 2006  Luke Arno  <luke.arno@gmail.com>

this program is free software; you can redistribute it and/or
modify it under the terms of the gnu general public license
as published by the free software foundation; either version 2
of the license, or (at your option) any later version.

this program is distributed in the hope that it will be useful,
but without any warranty; without even the implied warranty of
merchantability or fitness for a particular purpose.  see the
gnu general public license for more details.

you should have received a copy of the gnu general public license
along with this program; if not, write to:

the free software foundation, inc., 
51 franklin street, fifth floor, 
boston, ma  02110-1301, usa.

luke arno can be found at http://lukearno.com/
-->

  <head profile="http://gmpg.org/xfn/11">
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
    <title>hAtom to Atom</title>
    <meta name="author" content="Luke Arno" />
    <style type="text/css">
body {
   font-family: "Trebuchet MS", "Bitstream Vera Sans", verdana, lucida, arial, helvetica, sans-serif;
   text-align: center;
   margin: 0px;
   padding: 0px;
}
h1 {
   margin: 0px;
   padding: 10px;
   background-color: #008;
   color: #fff;
}
h2, h3 {
   color: #008;
}
#content {
   text-align: left;
   padding: 30px;
}
.homepage {
   float: right;
}
.subtitle {
   margin: 0px;
   padding: 3px;
   background-color: #777;
   color: #eee;
}
a {
   text-decoration: none;
}
a:hover {
   text-decoration: underline;
}
.subtitle a {
   color: #fff;
   font-weight: 900;
}
input#url {
    width: 400px;
}
.errors {
    border: dashed 1px #a00;
    padding: 10px;
    margin-bottom: 10px;
}
.errors h4, p.error {
    color: #a00;
}
    </style>
  </head>
  <body>

<div class="header">
  <h1 class="title">
    hatom2atom
  </h1>
  <p class="subtitle">Convert <a href="http://microformats.org/wiki/hatom" title="hAtom">hAtom</a> to <a href="http://www.ietf.org/rfc/rfc4287" title="Atom Syntax">Atom</a>.</p>
</div>
<div id="content">

  <a href="/" title="Home" class="homepage">Home</a>
  <h2>Description</h2>
  <p>
    <a href="http://www.python.org/pypi/hatom2atom" title="download from cheeseshop">hatom2atom</a> 
    provides Python tools for use with hAtom2Atom.xsl.
    Includes a test runner that uses html/atom
    file pairs to test for expected output and a WSGI app that
    acts as a proxy to transform hAtom documents into Atom
    (that you are looking at now).
  </p>
  <h3>hAtom2Atom.xsl</h3>
  <p>
    The latest version of hAtom2Atom.xsl is available at 
    <a href="http://rbach.priv.at/hAtom/" title="hAtom-2-Atom">http://rbach.priv.at/hAtom/</a>.
  </p>
  <h3>Try It:</h3>
  <div py:if="messages" class="errors">
    <h4>Error:</h4>
    <p py:for="message in messages" class="error">${message}</p>
  </div>
  <form method="GET">
    <fieldset>
      <legend>Enter the URL of an hAtom document and recieve Atom output.</legend>
      <label for="url">URL: <input type="text" id="url" name="url" value="${url}"/></label>
      <input type="hidden" name="ctype" id="ctype" value="text/xml"/>
      <input type="submit"/>
    </fieldset>
  </form>
  <p>
    Questions, comments, suggestions, bugs... :
    <a class="email" href="mailto:luke.arno@gmail.com">luke.arno@gmail.com</a>
  </p>
</div>

  </body>
</html>

