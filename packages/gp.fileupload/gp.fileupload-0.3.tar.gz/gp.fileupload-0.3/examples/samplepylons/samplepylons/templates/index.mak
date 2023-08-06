<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN"
   "http://www.w3.org/TR/html4/loose.dtd">
<html>
<head>
  <title>Pylons Default Page</title>
  <style>
    body { background-color: #fff; color: #333; }
    body, p {
      font-family: verdana, arial, helvetica, sans-serif;
      font-size:   12px;
      line-height: 18px;
    }
    a { color: #000; }
    a:visited { color: #666; }
    a:hover { color: #fff; background-color:#000; }
  </style>
  ${h.javascript_include_tag('/gp.fileupload.static/jquery.js')}
  ${h.javascript_tag('''
  jQuery(document).ready(function() {
      jQuery("form[enctype^='multipart/form-data']").fileUpload();
      jQuery("#sample").fileUpload({action: "/upload/save"});
  });
  ''')}

</head>
<body>

<h1>Welcome to your Pylons Web Application</h1>

<h3>Wrapping an existing form</h3>
<form action="/upload/save" enctype="multipart/form-data" method="POST">
    <input type="file" name="file1" /><br/>
    <input type="submit" />
</form>

<h3>A pure javascript form</h3>
<div id="sample"></div>

<div>&nbsp;</div>

</body>
</html>
