<?xml version="1.0" encoding="UTF-8"?>
<stl:block xmlns="http://www.w3.org/1999/xhtml" xmlns:stl="http://www.hforge.org/xml-namespaces/stl">



<form method="post" action=";edit_timetables" id="edit_timetables">
  <fieldset>
    <legend>Edit the timetable grid</legend>
    <p>
    You can specify timetables to limit the range when an event can be set.
    </p>
    <table class="form">
      <tr stl:repeat="timetable timetables">
        <td>
          <input class="checkbox" type="checkbox" name="ids" value="${timetable/index}"></input>
        </td>
        <td>
          From <input value="${timetable/start}" name="${timetable/startname}" size="5" maxlength="5" type="text"></input>
        </td>
        <td style="padding-left: 10px;">
          to <input value="${timetable/end}" name="${timetable/endname}" size="5" maxlength="5" type="text"></input>
        </td>
      </tr>
      <tr>
        <td></td>
        <td>
          From <input value="--:--" name="new_start" size="5" maxlength="5" type="text"></input>
        </td>
        <td style="padding-left: 10px;">
          to <input value="--:--" name="new_end" size="5" maxlength="5" type="text"></input>
          <input value="Agregar" class="button_add" name=";add" type="submit"></input>
        </td>
      </tr>
    </table>

    <br></br>
    <input value="Suprimir" class="button_delete" name=";remove" type="submit"></input>
    <input value="Update" class="button_ok" name=";update" type="submit"></input>
  </fieldset>
</form>

</stl:block>
