<!doctype html>
<html>
<head>
<title>${title}</title>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
<link rel="stylesheet" href="coredoc.css">
<style>
h3 { font-weight: bold; font-style: italic }
h3::before { font-style: normal }
.string { color: #600; }
.comment { color: #060; text-decoration: none; }
.comment a { color: #066; text-decoration: underline; }


body > pre
{
  border: 1px solid #ccc;
  background-color: hsl(0, 0%, 98%);
  white-space: pre-wrap;
  margin: 1.5em 0;
  padding: .5em;
}
.message-class
{
  color: #00c;
  font-weight: bold;
}

.int
{
  color: #006;
  font-weight: bold;
}
/*
.string
{
  color: green;
  font-weight: bold;
}
.bool
{
  color: pink;
  font-weight: bold;
}
.comment
{
  color: #999;
}
a
{
  text-decoration: none;
  color: #666;
}
a:hover
{
  color: #000;
  text-decoration: underline;
}
*/
</style>
% for script in scripts:
  % if 'src' in script:
<script src="${script['src']}"></script>
  % else:
<script>${script['text']}</script>
  % endif
% endfor
<body>
<p class="logo"><img src="http://www.opera.com/media/images/logo/ologo_wback.gif"></p>

