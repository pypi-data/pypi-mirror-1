<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
                    "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">

<head>
<meta content="text/html; charset=UTF-8" http-equiv="content-type" py:replace="''"/>
<title>Login Form</title>
</head>

<body>
  <h2>Please log in</h2>

  <form action="${h.url('/login_handler', came_from=c.came_from, __logins=c.login_counter)}"
        method="POST">
    <label for="login">Username:</label><input type="text" id="login" name="login" /><br/>
    <label for="password">Password:</label><input type="password" id="password" name="password" />
    <input type="submit" value="Login" />
  </form>
</body>
</html>