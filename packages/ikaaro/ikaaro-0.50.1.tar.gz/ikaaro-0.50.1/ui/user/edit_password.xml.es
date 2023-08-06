<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<stl:block xmlns="http://www.w3.org/1999/xhtml" xmlns:stl="http://www.hforge.org/xml-namespaces/stl">

<form method="post" action=";edit_password" name="edit_password">
  <fieldset>
    <legend>Edit Password</legend>
    <dl>
      <dt><label for="newpass">New Password</label></dt>
      <dd>
        <input id="newpass" name="newpass" type="password"></input>
      </dd>
      <dt><label for="confirm">Confirm</label></dt>
      <dd>
        <input id="newpass2" name="newpass2" type="password"></input>
      </dd>
      <stl:block stl:if="must_confirm">
        <dt>
          <label for="password" style="font-weight: bold">
            To confirm these changes, you must type your current password
          </label>
        </dt>
        <dd>
          <input id="password" name="password" type="password"></input>
        </dd>
      </stl:block>
    </dl>
    <input value="Save Changes" class="button_ok" type="submit"></input>
  </fieldset>
</form>

<script type="text/javascript">
  $("#newpass").focus();
</script>

</stl:block>
