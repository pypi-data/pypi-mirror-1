<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml"
      xmlns:py="http://genshi.edgewall.org/" py:strip="">

  <py:match path="head" once="true">
    <head py:attrs="select('@*')">
      <title py:with="title = list(select('title/text()'))">
        New Haus App<py:if test="title">: ${title}</py:if>
      </title>
      <link rel="stylesheet" 
            type="text/css" 
            href="/${package_name}/default.css"/>
      ${select('*[local-name()!="title"]')}
    </head>
  </py:match>

  <py:match path="body" once="true">
    <body py:attrs="select('@*')"><div id="wrap">
      <div id="header">
        <p>New Haus App</p>
      </div>
      <div id="content">
        ${select('*|text()')}
      </div>
      <div id="footer">
        <hr />
        <p class="powered-by-haus">
          Powered by <a href="http://houseofhaus.org/">Haus</a>
        </p>
      </div>
    </div></body>
  </py:match>

</html>

