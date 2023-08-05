<?xml version='1.0' encoding='utf-8'?>
<html xmlns="http://www.w3.org/1999/xhtml"
      xmlns:py="http://purl.org/kid/ns#"
>
  <head profile="http://gmpg.org/xfn/11">
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
    <title>RDFa To RDF proxy</title>
    <style media="all" type="text/css">
body {
background-color:#FFFAF5;
font-family:"Trebuchet MS","Bitstream Vera Sans",verdana,lucida,arial,helvetica,sans-serif;
margin:0pt;
padding:0pt;
text-align:center;
}
h1 {
background-color:#993300;
color:#FFFFFF;
margin:0px;
padding:10px;
}
h2, h3 {
color:#993300;
}
#content {
padding:30px;
text-align:left;
}

.content{text-align:left;padding:30px;}

.homepage {
float:right;
margin:0pt;
padding:0pt;
}
.subtitle {
background-color:#CC6600;
color:#EEEEEE;
margin:0px;
padding:5px;
}
a {
color:#CC6600;
text-decoration:none;
}
a:hover {
text-decoration:underline;
}
.subtitle a {
color:#FFFFFF;
font-weight:900;
}
input#url {
width:400px;
}
.errors {
border:1px dashed #AA0000;
margin-bottom:10px;
padding:10px;
}
.errors h4, p.error {
color:#AA0000;
}
    </style>
  </head>
  <body>

<div class="header">
  <h1 class="title">
    RDFa2RDF
  </h1>
  <p class="subtitle">Convert <a href="http://www.w3.org/MarkUp/2007/ED-rdfa-syntax-20070906/" title="RDFa">RDFa</a> to <a href="http://www.w3.org/RDF/" title="RDF">RDF</a>.</p>
</div>
<div id="content">

  <a href="/" title="Home" class="homepage">Home</a>
  <h2>Description</h2>
  <p>
  This Is a <a href="http://www.w3.org/2001/sw/grddl-wg/">GRDDL</a> proxy implementing <a href="http://www-sop.inria.fr/edelweiss/people/Fabien.Gandon/wakka.php?wiki=FabienGandon">Fabien Gandon</a>'s RDFa2RDF stylesheet. 
  </p>
  <h3>RDFa2RDFXML.xsl</h3>
  <p>
    The latest version of RDFa2RDFXML.xsl is available at 
    <a href="http://ns.inria.fr/grddl/rdfa/2007/09/12/RDFa2RDFXML.xsl" title="RDFa2RDFXML.xsl">http://ns.inria.fr/grddl/rdfa/2007/09/12/RDFa2RDFXML.xsl</a>.
  </p>
  <h3>Try It:</h3>
  <div py:if="messages" class="errors">
    <h4>Error:</h4>
    <p py:for="message in messages" class="error">${message}</p>
  </div>
  <form method="GET">
    <fieldset>
      <legend>Enter the URL of an RDFa document and recieve RDF output.</legend>
      <label for="url">URL: <input type="text" id="url" name="url" value="${url}"/></label>
      <br/>
      <label for="ctype">Content-Type:</label>
      <select name="ctype" id="ctype">
        <option value="application/xml">application/xml</option>
        <option value="text/xml">text/xml</option>
        <option value="application/rdf+xml">application/rdf+xml</option>
      </select>
      <label py:if="has_tidy" for="tidy">Tidy:</label>
      <select py:if="has_tidy" name="tidy" id="tidy">
        <option value="yes">yes</option>
        <option value="no">no</option>
      </select>
      <br/>
      
      <input type="submit"/>
    </fieldset>
  </form>
<p><img src="http://weborganics.co.uk/files/haudio_files/rdf_w3c_button.32.gif" alt="RDF icon" title="RDF"/> <img src="http://weborganics.co.uk/images/xhtml-rdfa-blue.png" alt="RDFa"/> </p>
</div>

  </body>
</html>

