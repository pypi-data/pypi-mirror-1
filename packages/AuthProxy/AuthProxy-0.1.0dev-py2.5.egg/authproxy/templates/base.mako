<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN"
  "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">
<html>
  <head>
    <title>QuickWiki</title>
    ${h.stylesheet_link_tag('/quick.css')}
    ${h.javascript_include_tag('/javascripts/effects.js', builtins=True)}
  </head>
  <body>
    <div class="content">
      ${next.body()}\
      <p class="footer">
        Return to the
        ${h.link_to('FrontPage', h.url_for(action="index", title="FrontPage"))}
        | ${h.link_to('Edit ' + c.title, h.url_for(title=c.title, action='edit'))}
      </p>
    </div>
  </body>
</html>

