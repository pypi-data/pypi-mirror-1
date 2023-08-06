<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#"
    py:extends="'master.kid'">
<head>
<meta content="text/html; charset=utf-8" http-equiv="Content-Type" py:replace="''"/>
<title>Zoner: ${zonename} archived serial ${soa.serial}</title>
</head>
<body>

  <h2>Archived Zone: ${zonename} (Serial: ${soa.serial})</h2>
  
  <div id="sidebar" py:if="not tg.identity.anonymous">
    <h2>Zone Options</h2>
    <ul class="links">
      <li><a href="revert?zone=${zonename}&amp;archive=${archivename}">Revert zone to this version</a></li>
    </ul>
  </div>
  
  <div>
    
    <div id="zone_soa" class="zone_box">
      <h4> SOA - <a href="editsoa?zone=${zonename}">edit</a> </h4>
      <table border="0">
        <tr> <td>Primary Master Server (MNAME):</td> <td><b>${soa.mname}</b></td> </tr>
        <tr class="even"> <td>Admin E-mail Address (RNAME):</td> <td> <b>${soa.rname}</b> </td></tr>
        <tr> <td>Serial Number:</td> <td> <b>${soa.serial}</b></td></tr>
        <tr class="even"> <td>Refresh (seconds):</td> <td> <b>${soa.refresh}</b> </td></tr>
        <tr> <td>Retry (seconds):</td> <td> <b>${soa.retry}</b> </td></tr>
        <tr class="even"> <td>Expire (seconds):</td> <td> <b>${soa.expire}</b> </td></tr>
        <tr> <td>Minimum TTL (seconds):</td> <td> <b>${soa.minttl}</b> </td></tr>
      </table>
    </div>
    
    <div id="hostnames_soa" class="zone_box">
      <h4> Host names - <a href="editzone?zone=${zonename}">edit</a> </h4>

      <div py:for="i,hostname in enumerate(hostnames)" py:strip="">
        <table py:attrs="{'class': ['odd', 'even'][i%2]}">
          <tr>
            <td width="30%" valign="top">
              <b>${hostname}</b>
            </td>
            <td>
              <table py:for="(type, description) in ( ('A', 'A (Address)'), ('NS', 'NS (Name Server)'), ('MX', 'MX (Mail Exchange)'), ('CNAME', 'CNAME (Canonical Name)'), ('TXT', 'TXT (Text)') )">
                <tr py:if="names[hostname].records(type)">
                  <td width="40%" valign="top">
                    ${description}
                  </td>
                  <td valign="top">
                    <div py:for="r in names[hostname].records(type).items">
                      <div py:if="type != 'MX'">
                        ${r}
                      </div>
                      <div py:if="type == 'MX'">
                        ${r[0]} ${r[1]}
                      </div>
                    </div>
                  </td>
                </tr>
              </table>
            </td>
          </tr>
        </table>
      </div>
    </div>

  </div>

</body>
</html>
