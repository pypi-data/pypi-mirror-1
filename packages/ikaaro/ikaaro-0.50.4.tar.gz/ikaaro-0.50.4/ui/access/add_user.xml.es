<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<stl:block xmlns="http://www.w3.org/1999/xhtml" xmlns:stl="http://www.hforge.org/xml-namespaces/stl">

  <form method="post" action=";add_user" name="addform">
    <fieldset>
      <legend>Agregar un nuevo usuario</legend>
      <dl>
        <dt>Correo electrónico</dt>
        <dd>
          <input id="email" name="email" size="40" type="text"></input>
        </dd>
        <stl:block stl:if="is_admin">
          <dt>Contraseña</dt>
          <dd>
            <input id="newpass" name="newpass" type="password"></input>
          </dd>
          <dt>Repeat Password</dt>
          <dd>
            <input id="newpass2" name="newpass2" type="password"></input>
          </dd>
        </stl:block>
        <dt>Choose the role for the new member</dt>
        <dd>
          <select name="role">
            <option value="${role/name}" stl:repeat="role roles">${role/title}</option>
          </select>
        </dd>
      </dl>
      <input value="Agregar y ver" type="submit" name="add_and_view" class="button_ok"></input>
      <input value="Agregar y regresar" name="add_and_return" type="submit"></input>
    </fieldset>
  </form>

  <script language="javascript">
    $("#email").focus();
  </script>

</stl:block>
