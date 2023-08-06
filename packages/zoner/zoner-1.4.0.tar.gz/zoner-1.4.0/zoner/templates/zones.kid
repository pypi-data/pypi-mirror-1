<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#"
    py:extends="'master.kid'">
<head>
<meta content="text/html; charset=utf-8" http-equiv="Content-Type" py:replace="''"/>
<title>Zoner: Manage Zones</title>
</head>
<body>

  <div id="sidebar">
    <h2>Learn More</h2>
    Useful resources about DNS &amp; Zone Management:
    <ul class="links">
      <li><a href="http://en.wikipedia.org/wiki/Domain_name_system">Wikipedia explanation of DNS</a></li>
      <li><a href="http://tools.ietf.org/html/rfc1034">RFC 1034: Domain Names - Concepts and Facilities</a></li>
      <li><a href="http://tools.ietf.org/html/rfc1035">RFC 1035: Domain Names - Implementation and Specification</a></li>
    </ul>
  </div>
  
  <div>
    <p>
      <span py:replace="zonecount">0</span> DNS Zones are available for management:

      <ul py:for="zone in zones">
        <li> <a href="#" py:attrs="'href':'manage?zone=%s'%zone" py:content="zone" /> </li>
      </ul>

    </p>
    
    <p>
      <br />
      <br />
      <br />
      <br />
      <br />
      <br />
      <br />
    </p>
  </div>

</body>
</html>
