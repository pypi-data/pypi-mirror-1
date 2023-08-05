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
  <form action="">
      <input type="hidden" name="v_id" value="${v_id}" />
      <input type="hidden" name="r_id" value="${r_id}" />
      <input type="hidden" name="action" value="${action}" />
      <dl>
          <dt>Name</dt>
          <dd><input name="name" value="${server.name}" /></dd>
          <dt>IP Address</dt>
          <dd><input name="ip_address" value="${server.ip_address}" /></dd>
          <dt>Port</dt>
          <dd><input name="port" value="${server.port}" /></dd>
          <!--
          <dt>Cookie</dt>
          <dd><input name="cookie" value="${server.parent.persist}" /></dd>
          -->
          <dt>Options</dt>
          <dd><input name="options" value="${server.options}" /></dd>
      </dl>
      <input type="submit" value="submit" />
  </form>
  <div py:replace="list_servers(virtuals)" />
</div>

</body>
</html>

