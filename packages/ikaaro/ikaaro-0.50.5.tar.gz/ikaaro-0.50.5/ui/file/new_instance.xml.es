<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<stl:block xmlns="http://www.w3.org/1999/xhtml" xmlns:stl="http://www.hforge.org/xml-namespaces/stl">

<form method="post" action=";new_resource?type=${class_id}" name="new_resource" enctype="multipart/form-data">
  <fieldset>
    <legend>Upload a ${class_title}</legend>
    <dl>
      <dt><label for="title">Title</label></dt>
      <dd>
        <input id="title" value="${title}" name="title" size="40" type="text"></input>
      </dd>
      <dt><label for="file">Fichero</label></dt>
      <dd>
        <input id="file" name="file" size="35" type="file"></input>
      </dd>
    </dl>
    <input value="Upload" class="button_ok" type="submit"></input>
  </fieldset>
</form>

</stl:block>
