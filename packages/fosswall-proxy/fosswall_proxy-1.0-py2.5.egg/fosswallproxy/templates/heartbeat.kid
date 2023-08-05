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
          <dt>Serial</dt>
          <dd><input name="serial" value="${conf.serial}" /></dd>
          <dt>Bcast</dt>
          <dd><input name="bcast" value="${conf.bcast}" /></dd>
          <dt>Keepalive</dt>
          <dd><input name="keepalive" value="${conf.keepalive}" /></dd>
          <dt>Deadtime</dt>
          <dd><input name="deadtime" value="${conf.deadtime}" /></dd>
          <dt>Warntime</dt>
          <dd><input name="warntime" value="${conf.warntime}" /></dd>
          <dt>Ping Node</dt>
          <dd><input name="ping" value="${conf.ping}" /></dd>
          <dt>Auto Failback</dt>
          <!--dd><input name="auto_failback" value="${conf.auto_failback}" /></dd-->
		  <dd><select name="auto_failback">
			  <option py:for="v in ('on', 'off')" py:if="conf.auto_failback == v"
			  selected="selected"
			  value="${v}">${v}</option>
			  <option py:for="v in ('on', 'off')" py:if="conf.auto_failback != v"
			  value="${v}">${v}</option>
		  </select></dd>
      </dl>
      <input type="submit" value="submit" />
  </form>
</div>

</body>
</html>

