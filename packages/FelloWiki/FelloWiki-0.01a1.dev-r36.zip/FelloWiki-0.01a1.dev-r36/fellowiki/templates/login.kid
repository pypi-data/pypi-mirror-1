<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<!--! 
Copyright (c) 2006 Jan Niklas Fingerle

This source code file is based on a TurboGears "quickstarted" project.
The TurboGears framework is copyrighted (c) 2005, 2006 by Kevin Dangoor 
and contributors.

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
-->

<html xmlns="http://www.w3.org/1999/xhtml"
      xmlns:py="http://purl.org/kid/ns#"
      py:extends="'master.kid'">

    <head>
        <meta content="text/html; charset=UTF-8"
              http-equiv="content-type" />
        <title>Login</title>
    </head>

    <body>
        <div id="loginBox">
            <h1>Login</h1>
            <p>${message}</p>
            <form action="${previous_url}" method="POST">
                <table>
                    <tr>
                        <td class="label">
                            <label for="user_name">User Name:</label>
                        </td>
                        <td class="field">
                            <input type="text" id="user_name" name="user_name"/>
                        </td>
                    </tr>
                    <tr>
                        <td class="label">
                            <label for="password">Password:</label>
                        </td>
                        <td class="field">
                            <input type="password" 
                                   id="password" 
                                   name="password"/>
                        </td>
                    </tr>
                    <tr>
                        <td colspan="2" class="buttons">
                            <input type="submit" name="login" value="Login"/>
                        </td>
                    </tr>
                </table>

                <input py:if="forward_url" type="hidden" name="forward_url"
                       value="${forward_url}"/>
                
                <input py:for="name,value in original_parameters.items()"
                       type="hidden" name="${name}" value="${value}"/>
            </form>
        </div>
    </body>
</html>
