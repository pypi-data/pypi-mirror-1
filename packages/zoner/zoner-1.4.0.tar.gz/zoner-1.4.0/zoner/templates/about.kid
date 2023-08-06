<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#"
    py:extends="'master.kid'">
<head>
<meta content="text/html; charset=utf-8" http-equiv="Content-Type" py:replace="''"/>
<title>Zoner: About</title>
</head>
<body>
  
  <div class="about">
    <p> Zoner is an open source DNS zone management UI. </p>
    
    <p> Zoner is written in <a href="http://python.org/">Python</a> using the <a href="http://turbogears.org">TurboGears</a> web framework. </p>
    
    <p> Zoner is a project by <a href="http://chrismiles.info/">Chris Miles</a>. </p>
    
    <p> Version ${version} </p>
    
    <p class="about_logos">
      <a href="http://www.python.org/"><img src="${tg.url('/static/images/python-powered-w-100x40.png')}" alt="Python Powered" /></a>
      <a href="http://www.turbogears.org/"><img src="${tg.url('/static/images/under_the_hood_blue.png')}" alt="TurboGears under the hood" /></a>
    </p>
    
  </div>

</body>
</html>
