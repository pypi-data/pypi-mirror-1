<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#"
py:extends="'master.kid'">

<head>
    <meta content="text/html; charset=UTF-8" http-equiv="content-type" py:replace="''"/>
    <title>Welcome to TurboGears</title>
</head>

<body>
    <table>
        <tr py:for="tg_col in tg_columns">
          <td py:content="tg_col[0]">Column Name</td>
          <td py:content="getattr(self, tg_col[1])">Column Data</td>
        </tr>
    </table>
</body>
</html>
