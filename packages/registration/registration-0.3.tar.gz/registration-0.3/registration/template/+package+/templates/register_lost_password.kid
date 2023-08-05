<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#"
    py:extends="'master.kid'">

<head>
    <meta content="text/html; charset=UTF-8" http-equiv="content-type" py:replace="''"/>
    <title>Lost Password</title>
</head>

<body>
    <!-- !Policy is to reset password -->
    <span py:if="policy=='reset'" py:strip="True">
        <h1>Reset Password</h1>

        <p>
            Please enter the user name or email address associated with your account.  Your 
            password will be reset and your new password will be emailed to you.
        </p>
        <?python
        submit_text = 'Reset Password'
        ?>
    </span>
    
    <!-- !Policy is to send current password -->
    <span py:if="policy=='send_current'" py:strip="True">
        <h1>Lost Password</h1>
        
        <p>
            Please enter the user name or email address associated with your account.  
            We will email your password to you.
        </p>
        
        <?python
        submit_text = 'Email Password'
        ?>
    </span>
    
    <p py:content="form(action=action, submit_text=submit_text)">Lost Password form goes here</p>

</body>
</html>
