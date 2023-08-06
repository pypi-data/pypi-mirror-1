<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#"
    py:extends="'master.kid'">

<head>
    <meta content="text/html; charset=UTF-8" http-equiv="content-type" py:replace="''"/>
    <title py:content="'Zoner: ' + zonename + u' - ' + _(u'Revert to serial %s') %archived_zone.root.soa.serial" />
</head>

<body>
  <div>
    <h4 py:content="zonename + u' : ' + _(u'Revert to serial %s') %archived_zone.root.soa.serial" />
    
    Revert zone ${zonename} back to version ${archived_zone.root.soa.serial} ?
    
    <p py:content="form(method='GET', action=action, yes_text=yes_text, no_text=no_text, value=value, options=options)">Form goes here</p>
  </div>
</body>
</html>