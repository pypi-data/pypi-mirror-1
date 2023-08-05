<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<?python import sitetemplate ?>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#" py:extends="sitetemplate">

<head py:match="item.tag=='{http://www.w3.org/1999/xhtml}head'" py:attrs="item.items()">
    <meta content="text/html; charset=UTF-8" http-equiv="content-type" py:replace="''"/>
    <title py:replace="''">Your title goes here</title>
    <meta py:replace="item[:]"/>
    <style type="text/css">
        #pageLogin
        {
            font-size: 10px;
            font-family: verdana;
            text-align: right;
        }
    </style>
    <style type="text/css" media="screen">
@import url('/static/css/style.css');
</style>
<script language="javascript" type="text/javascript">
    <!--
    var message;
    function areyousure(message)
    { // Generic function to confirm a request
        if (confirm(message))
        {
            return true
        }
        else
        {
            return false
        }

    }

    //-->
</script>
</head>

<body py:match="item.tag=='{http://www.w3.org/1999/xhtml}body'" py:attrs="item.items()">
    <div py:if="tg.config('identity.on') and not defined('logging_in')" id="pageLogin">
        <span py:if="tg.identity.anonymous">
            <a href="${tg.url('/login')}">Login</a>
        </span>
        <span py:if="not tg.identity.anonymous">
            Welcome ${tg.identity.user.display_name}.
            <a href="${tg.url('/logout')}">Logout</a>
        </span>
    </div>
    <div id="header">&nbsp;</div>
    <div id="main_content">
    <div id="status_block" class="flash" py:if="value_of('tg_flash', None)" py:content="tg_flash"></div>

<table py:def="list_servers(virtuals)">
    <thead>
    <tr><td colspan="6"><a href="virtual_new">Add Virtual Server</a></td></tr>
    <tr>
      <th></th>
      <th>Name</th>
      <th>IP Address</th>
      <th>Port</th>
      <th></th>
      <th></th>
    </tr>
    </thead>
    <?python
    v_cnt = 0
    ?>
    <tbody py:for="listen in virtuals">
      <?python
      v_cnt += 1
      v_args = 'v_id=%s' % (v_cnt-1)
      ?>
      <tr>
         <th>VIP ${v_cnt}</th>
         <th>${listen.name}</th>
         <th>${listen.ip_address}</th>
         <th>${listen.port}</th>
         <th><a href="virtual_modify?${v_args}">Modify</a></th>
         <th><a href="virtual_remove?${v_args}"
                 onclick="return areyousure('Are you sure you want to remove the virtual server ${listen.name} (${listen.ip_address}:${listen.port})?')">Remove</a></th>
      </tr>
      <tr><td colspan="6"><a href="real_new?${v_args}">Add Real Server</a></td></tr>
      <?python
      r_cnt = 0
      ?>
      <tr py:for="server in listen.server">
          <?python
          r_cnt += 1
          r_args = 'v_id=%s&r_id=%s' % (v_cnt-1, r_cnt-1)
          ?>
          <td>RIP ${r_cnt}</td>
          <td>${server.name}</td>
          <td>${server.ip_address}</td>
          <td>${server.port}</td>
          <td><a href="real_modify?${r_args}">Modify</a></td>
          <td><a href="real_remove?${r_args}"
                 onclick="return areyousure('Are you sure you want to remove the real server ${server.name} (${server.ip_address}:${server.port})?')">Remove</a></td>
          <td></td>
      </tr>
      <tr><td colspan="6">&nbsp;</td></tr>
    </tbody>
</table>

<table py:def="list_ssl(servers)">
    <thead>
      <tr><td colspan="6"><a href="ssl_new">Add SSL Termination</a></td></tr>
      <tr>
        <th></th>
        <th colspan="2">Virtual</th>
        <th></th>
        <th colspan="2">Backend</th>
        <th></th>
        <th></th>
      </tr>
      <tr>
        <th></th>
        <th>IP Address</th>
        <th>Port</th>
        <th></th>
        <th>IP Address</th>
        <th>Port</th>
        <th></th>
        <th></th>
      </tr>
      </thead>
    <tbody>
      <?python
      v_cnt = 0
      ?>
      <tr py:for="listen in servers">
          <?python
          v_args = 'id=%s' % (v_cnt)
          v_cnt += 1
          service = listen.service
          ?>
          <th>VIP ${v_cnt}</th>
          <td>${listen.Address.value}</td>
          <td>${listen.Port.value}</td>
          <td> -&gt; </td>
          <td>${service.Address.value}</td>
          <td>${service.Port.value}</td>
          <th><a href="ssl_modify?${v_args}">Modify</a></th>
          <th><a href="ssl_remove?${v_args}"
                 onclick="return areyousure('Are you sure you want to remove the ssl termination ${listen.Address.value}:${listen.Port.value}?')">Remove</a></th>
      </tr>
    </tbody>
</table>

  <div id="sidebar">
      <ul>
          <li><a href="/view" title="View Configurations">View Configurations</a></li>
          <li><a href="/edit" title="Edit Configurations">Edit Configurations</a></li>
          <li><a href="/maintenance" title="Maintenance">Maintenance</a></li>
          <li><a href="/reports" title="Show Reports">Show Reports</a></li>
      </ul>
  </div>

    <div py:replace="[item.text]+item[:]"/>

    <!-- End of main_content -->
    </div>
<!--
-->
<div id="footer">
  <p>TurboGears is a open source front-to-back web development
    framework written in Python</p>
  <p>Copyright &copy; 2007 Kevin Dangoor</p>
</div>
</body>

</html>
