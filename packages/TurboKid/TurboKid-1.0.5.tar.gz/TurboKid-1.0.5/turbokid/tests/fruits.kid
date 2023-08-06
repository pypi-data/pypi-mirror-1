<html xmlns:py="http://purl.org/kid/ns#">
  <head>
    <title py:content="title">This is replaced.</title>
  </head>
  <body>
    <p>These are some of my favorite fruits:</p>
    <ul>
      <li py:for="fruit in fruits">
        I like ${fruit}s
      </li>
    </ul>
  </body>
</html>
