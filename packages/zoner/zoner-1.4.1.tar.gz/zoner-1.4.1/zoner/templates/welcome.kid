<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#"
    py:extends="'master.kid'">
<head>
<meta content="text/html; charset=utf-8" http-equiv="Content-Type" py:replace="''"/>
<title>Zoner</title>
</head>
<body>

  <div id="sidebar">
    <h2>Menu</h2>
    <ul class="links">
      <li><a href="zone/">Manage Zones</a></li>
      <li><a href="about">About</a></li>
    </ul>
  </div>
  
  <div>
    Welcome to Zoner - the DNS Zone Management UI.

    <p py:if="tg.identity.anonymous"> You must <a href="login">login</a> to use this software. </p>
  </div>

</body>
</html>
