<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#"
    py:extends="'../master.kid'">

<head>
    <meta content="text/html; charset=UTF-8" http-equiv="content-type" py:replace="''"/>
    <title>Edit User Information</title>
</head>

<body>
    <h1>Edit ${display_name}'s Information</h1>
    
    <p py:content="form.display(action=action, value=form_values, submit_text=u'Update Info')">Existing user form goes here</p>

</body>
</html>