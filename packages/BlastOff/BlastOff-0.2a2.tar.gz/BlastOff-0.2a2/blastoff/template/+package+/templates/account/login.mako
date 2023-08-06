<%inherit file="/base/base-index.mako"/>

<%def name="title()">Login</%def>

<form action="/account/dologin" method="POST">
  Username: <input type="text" name="login" value="" />
  <br />
  Password: <input type="password" name="password" value ="" />
  <br />
  <input type="submit" value="Login" />
</form>
