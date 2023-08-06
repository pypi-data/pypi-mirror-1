<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#"
    py:extends="'master.kid'">
<head>
<meta content="text/html; charset=utf-8" http-equiv="Content-Type" py:replace="''"/>
<title py:content="zonename + u' : ' + _(u'Edit Zone')" />
</head>
<body>

  <h2 py:content="_(u'Edit Zone for ') + zonename" />
  <div>
    
    <p py:content="form(action=action, submit_text=submit_text, value=value, options=options, attrs=attrs)">Form goes here</p>

  </div>

</body>
</html>
