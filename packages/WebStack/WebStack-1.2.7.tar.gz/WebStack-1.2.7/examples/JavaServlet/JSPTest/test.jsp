<html>
  <head>
    <title>Test of JSP</title>
  </head>
  <body>
    <p>Hello <%= request.getAttribute("hello") %>! (attribute "hello")</p>
    <p>Goodbye <%= request.getParameter("hello") %>! (parameter "hello")</p>
  </body>
</html>
