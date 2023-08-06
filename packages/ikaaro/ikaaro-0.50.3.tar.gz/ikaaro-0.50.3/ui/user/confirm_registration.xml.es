<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<stl:block xmlns="http://www.w3.org/1999/xhtml" xmlns:stl="http://www.hforge.org/xml-namespaces/stl">

  <p>
  ${confirmation_msg}<br></br>
  </p>

  <fieldset>
    <legend>Choose your password</legend>

  <form method="post" action=";confirm_registration" name="confirm_registration">
    <dl>
      <dt>
        <label for="username">Username</label>
      </dt>
      <dd>
        <strong>${username}</strong>
      </dd>
      <dt>
        <label for="newpass">Contraseña</label>
      </dt>
      <dd>
        <input id="newpass" name="newpass" type="password"></input>
      </dd>
      <dt>
        <label for="password2">Repetir contraseña</label>
      </dt>
      <dd>
        <input id="newpass2" name="newpass2" type="password"></input>
      </dd>
    </dl>
    <p>
      <input value="${key}" name="key" type="hidden"></input>
      <input value="Next" class="button_ok" type="submit"></input>
    </p>
  </form>

  <script language="javascript">
    $("#newpass").focus();
  </script>
  </fieldset>

</stl:block>
