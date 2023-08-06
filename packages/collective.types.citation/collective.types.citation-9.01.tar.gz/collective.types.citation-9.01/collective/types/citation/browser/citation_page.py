<!-- (C) 2005-2009. University of Washington. All rights reserved. -->

<html xmlns="http:///www.w3.org/1999/xhtml"
  xml:lang="en"
  xmlns:tal="http://xml.zope.org/namespaces/tal"
  xmlns:metal="http://xml.zope.org/namespaces/metal"
  xmlns:i18n="http://xml.zope.org/namespaces/i18n"
  lang="en"
  metal:use-macro="context/main_template/macros/master"
  i18n:domain="myph.types">
  
  <body>

    <metal:main fill-slot="main">
      
      <div tal:replace="structure view/getLayout" />
	        
    </metal:main>
  </body>
</html>
