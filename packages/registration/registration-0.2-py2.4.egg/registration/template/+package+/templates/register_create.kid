<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#"
    py:extends="'master.kid'">

<head>
    <meta content="text/html; charset=UTF-8" http-equiv="content-type" py:replace="''"/>
    <title>Registration Submitted</title>
</head>

<body>
    <h1>Saved Information for ${name}</h1>
    
    <p>
        We are sending an email to ${email} with additional instructions. Please follow 
        those directions in order to finalize your registration.
    </p>

	<!-- !If you have groups listed in 'registration.unverified_user.groups', then the user is now 
	logged in and an active user (in the groups specified).  You may want to put some information 
	here about what they can and can't do.  Or maybe not.  Your call.  :-)  -->
    
    <p>Thank you.</p>

</body>
</html>