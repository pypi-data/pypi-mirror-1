<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<stl:block xmlns="http://www.w3.org/1999/xhtml" xmlns:stl="http://www.hforge.org/xml-namespaces/stl">

<form name="loginform" method="post" action=";login" id="loginform">
  <fieldset>
    <legend>Identificarse</legend>
    <dl>
      <dt><label for="username">Dirección de correo electrónico</label></dt>
      <dd>
        <input id="username" type="text" name="username" value="${username}"></input>
      </dd>
      <dt><label for="password">Contraseña</label></dt>
      <dd>
        <input id="password" name="password" type="password"></input>
        <a href="/;forgotten_password">Olvidé mi contraseña</a>
      </dd>
    </dl>
    <input value="Identificarse" class="button_ok" type="submit"></input>
  </fieldset>

  <script language="javascript">
    <stl:inline stl:if="not username">$("#username").focus();</stl:inline>
    <stl:inline stl:if="username">$("#password").focus();</stl:inline>
  </script>
</form>

</stl:block>
