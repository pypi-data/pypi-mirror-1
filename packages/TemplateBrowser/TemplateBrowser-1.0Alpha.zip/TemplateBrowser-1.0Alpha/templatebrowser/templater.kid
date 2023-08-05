<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#" >
<head>
<title>Template Browser</title>
<link type="text/css" rel="stylesheet" href="/tg_static/css/toolbox.css">
</link>
<style type="text/css">
       code { color:#999; }
       .odd{background-color:#edf3fe}
       .even{background-color:#fff}
</style>
</head>
<body>
<div id="top_background">
  <div id="top">
    <h1> <a href="/">Toolbox</a> &#x00BB; Templates Browser </h1>
  </div>
</div>
<p> Click the template you want to browse: </p>
<div id="template_manager">
  <table width="100%" cellpadding="0" cellspacing="0" border="0">
    <tr py:for="idx,file in enumerate(project_files)" class="${idx%2 and 'odd' or 'even'}">
      <td><table cellpadding="0" cellspacing="0" border="0">
          <tr>
            <td>
              <img src="/tg_static/images/transp.png" width="${file['level']*20}" height="1" alt="" /> </td>
            <td>
              <img src="/tg_static/images/folder.png" py:if="file['isdir']" alt="" />
              <div py:if="file['isdir']" py:strip="">${file['file_name']}</div>
              <img src="/tg_static/images/file.png" py:if="not file['isdir']" alt="" />  
              <a href="preview/${file['file_name']}" target="_blank" py:if="not file['isdir']">${file['file_name']}</a> 
              <a href="plain/${file['file_name']}" target="_blank" py:if="not file['isdir']" >(txt)</a>
            </td>
          </tr>
        </table></td>
    </tr>
  </table>
  <br />
</div>
</body>
</html>
