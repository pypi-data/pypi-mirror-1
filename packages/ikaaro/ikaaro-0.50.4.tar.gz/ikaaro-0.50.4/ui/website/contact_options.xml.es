<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<stl:block xmlns="http://www.w3.org/1999/xhtml" xmlns:stl="http://www.hforge.org/xml-namespaces/stl">

<form action=";edit_contact_options" method="post">
  <fieldset>
    <legend>Edit Contact Options</legend>
    <dl>
      <dt><label for="contacts">Select the contact accounts</label></dt>
      <dd>
        <select id="contacts" name="contacts" size="15" multiple="multiple">
          <option value="${contact/name}" selected="${contact/is_selected}" stl:repeat="contact contacts">${contact/title} (${contact/email})</option>
        </select>
      </dd>
    </dl>
    <input value="Change" class="button_ok" type="submit"></input>
  </fieldset>
</form>

</stl:block>
