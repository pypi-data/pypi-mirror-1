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
      <input type="hidden" name="id" value="${id}" />
      <input type="hidden" name="action" value="${action}" />
      <dl>
          <dt>Virtual IP Address</dt>
          <dd><input name="v_ip" value="${listen.Address.value}" /></dd>
          <dt>Virtual Port</dt>
          <dd><input name="v_port" value="${listen.Port.value}" /></dd>
          <dt>Backend IP Address</dt>
          <dd><input name="r_ip" value="${listen.service.Address.value}" /></dd>
          <dt>Backend Port</dt>
          <dd><input name="r_port" value="${listen.service.Port.value}" /></dd>
      </dl>
      <input type="submit" value="submit" />
  </form>
  <div py:replace="list_ssl(servers)" />
</div>

</body>
</html>

