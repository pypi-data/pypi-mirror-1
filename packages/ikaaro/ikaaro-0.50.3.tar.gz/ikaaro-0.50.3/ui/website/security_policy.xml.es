<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<stl:block xmlns="http://www.w3.org/1999/xhtml" xmlns:stl="http://www.hforge.org/xml-namespaces/stl">

<form action=";edit_security_policy" method="post">
  <fieldset>
    <legend>Edit Security Policy</legend>
    <p>
      <input value="0" type="radio" id="intranet" name="website_is_open" checked="${is_closed}"></input>
      <label for="intranet">Intranet</label>  <br></br> Authentication will be required for any level of access. Only administrators will be able to register new users.
    </p>
    <p>
      <input value="1" type="radio" id="extranet" name="website_is_open" checked="${is_open}"></input>
      <label for="extranet">Extranet</label>  <br></br> Non authenticated users will be able to access published content, and to register by themselves.
    </p>
    <input value="Save Changes" class="button_ok" type="submit"></input>
  </fieldset>
</form>

</stl:block>
