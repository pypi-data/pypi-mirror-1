<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#"
    py:extends="'master.kid'">
<head>
<meta content="text/html; charset=utf-8" http-equiv="Content-Type" py:replace="''"/>
<title>${title}</title>
</head>
<body>

  <div id="main">
      <h1>${title}</h1>
      <ul>
          <li py:for="link,name in menu.iteritems()">
          <a href="${link}" title="${name}">${name}</a>
          </li>
      </ul>
  </div>

</body>
</html>
