<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<stl:block xmlns="http://www.w3.org/1999/xhtml" xmlns:stl="http://www.hforge.org/xml-namespaces/stl">

<form method="post" action="${action}" id="edit_event" stl:if="action">
  <p>(To add an event lasting all day long, leave time fields empty.)</p>
  <input value="${resource}" stl:if="resource" name="resource" type="hidden"></input>
  <table class="form">
    <tr stl:if="resources">
      <td>Resource</td>
      <td>
        <select name="resource">
          <option value="${item/name}" selected="{item/selected}" stl:repeat="item resources">${item/value} </option>
        </select>
      </td>
    </tr>
    <tr>
      <td>Summary</td>
      <td>
        <input id="SUMMARY" type="text" name="SUMMARY" value="${SUMMARY}"></input>
      </td>
    </tr>
    <tr>
      <td>Localización</td>
      <td>
        <input value="${LOCATION}" name="LOCATION" type="text"></input>
      </td>
    </tr>
    <tr>
      <td>Start</td>
      <td>
        <input name="dtstart" size="10" id="dtstart" maxlength="10" type="text" value="${dtstart}"></input>
        <input value="..." id="trigger_dtstart" type="button"></input>  
        <input name="dtstart_time" size="5" id="dtstart_time" maxlength="5" type="text" value="${dtstart_time}"></input>
      </td>
    </tr>
    <tr>
      <td>End</td>
      <td>
        <input name="dtend" size="10" id="dtend" maxlength="10" type="text" value="${dtend}"></input>
        <input value="..." id="trigger_dtend" type="button"></input>  
        <input name="dtend_time" size="5" id="dtend_time" maxlength="5" type="text" value="${dtend_time}"></input>
      </td>
    </tr>
    <tr>
      <td valign="top">Descripción</td>
      <td>
        <textarea name="DESCRIPTION" cols="65">${DESCRIPTION}</textarea>
      </td>
    </tr>

    <!-- STATUS -->
    <tr stl:if="STATUS">
      <td>Estado</td>
      <td>
        <select name="STATUS">
          <option value="${s/name}" selected="${s/selected}" stl:repeat="s STATUS">${s/value}</option>
        </select>
      </td>
    </tr>

    <!-- ATTENDEES -->
    <!--
    <tr stl:if="ATTENDEE">
      <td>Attendees</td>
      <td>
        <table stl:repeat="att ATTENDEE">
          <tr>
            <td>E-mail Address</td>
            <td colspan="3">
              <input type="text" size="30" name="${att/uri}"
                value="${att/v_uri}" />
            </td>
          </tr>
          <tr>
            <td>Common Name</td>
            <td>
              <input type="text" size="20" name="${att/common}"
                value="${att/v_common}" />
            </td>
            <td>Presence</td>
            <td>
              <select name="${att/role}">
                <stl:block stl:if="att/v_role/required">
                  <option selected="yes">REQUIRED</option>
                  <option>OPTIONNAL</option>
                  <option>NONE</option>
                </stl:block>
                <stl:block stl:if="att/v_role/optionnal">
                  <option>REQUIRED</option>
                  <option selected="yes">OPTIONNAL</option>
                  <option>NONE</option>
                </stl:block>
                <stl:block stl:if="att/v_role/no">
                  <option>REQUIRED</option>
                  <option>OPTIONNAL</option>
                  <option selected="yes">NONE</option>
                </stl:block>
              </select>
            </td>
          </tr>
          <tr></tr>
        </table>
      </td>
    </tr>
    -->

    <!-- COMMENTS -->
    <!--
    <tr stl:repeat="comment COMMENT">
      <td>Comment</td>
      <td>
        <textarea name="${comment/name}" cols="65">${comment/value}</textarea>
      </td>
    </tr>
    -->
  </table>

  <p stl:if="allowed">
     <input value="Aceptar" class="button_ok" name=";edit_event" type="submit"></input>
     <input value="Definitely remove" stl:if="remove" class="button_delete" name=";remove_event" type="submit"></input>
     <input value="Cancelar" stl:if="not remove" class="button_cancel" name=";cancel" type="submit"></input>
  </p>

  <script language="javascript">
  $("#SUMMARY").focus();

  Calendar.setup({inputField: "dtstart", ifFormat: "%Y-%m-%d",
    button: "trigger_dtstart"});
  Calendar.setup({inputField: "dtend", ifFormat: "%Y-%m-%d",
    button: "trigger_dtend"});
  </script>
</form>

</stl:block>
