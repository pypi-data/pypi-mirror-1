<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#"
    py:extends="'master.kid'">

<head>
    <meta content="text/html; charset=UTF-8" http-equiv="content-type" py:replace="''"/>
    <title>FileField</title>
</head>

<body>
    <div style="width: 40%">
    <p>This form will simulate a validation error so you can see how the file is 
    stored on the server side cache (on a secure temp file) allowing the user
    to resubmit without resending the file (only an id on a hidden field).</p>
    <p>The download url only works per session, that means that the user can 
    link it to other person and they won't be able to download it</p>
    <p>If you leave the fail field blank, the submit will succed and you will be 
    taken to the widgets page. (the file won't be saved anywere)</p>
    <p>Temporary files are automatically deleted when the session is cleared or expires, or when the server is taken down</p>
    </div>
    ${form.display()}
    <p>Don't upload big files (> 1 MB) here. The widget demo server will output
    everything the form passes including the file contents to the console, and 
    can be really slow.</p>
</body>
</html>
