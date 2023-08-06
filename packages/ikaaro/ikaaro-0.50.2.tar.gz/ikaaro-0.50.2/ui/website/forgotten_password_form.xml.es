<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<stl:block xmlns="http://www.w3.org/1999/xhtml" xmlns:stl="http://www.hforge.org/xml-namespaces/stl">

<form method="post" name="loginform" action=";forgotten_password" id="loginform">
  <fieldset>
    <legend>Si olvidaste tu contraseña</legend>
    <dl>
      <dt>
        <label for="username">Escribe tu dirección de correo electrónico</label>
      </dt>
      <dd>
        <input id="username" name="username" type="text"></input>
      </dd>
    </dl>
    <input value="Aceptar" class="button_ok" type="submit"></input>
  </fieldset>
  <script language="javascript">
    $("#username").focus();
  </script>
</form>


</stl:block>
