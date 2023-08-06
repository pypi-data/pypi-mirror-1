<html>
    <head>
        <title>QuickWiki</title>
        <% h.stylesheet_link_tag('/quick.css') %>
    </head>
    <body>
        <div class="content">
% m.call_next()
        <p class="footer">
            Return to the
            <% h.link_to('FrontPage', h.url_for(action="index", title="FrontPage")) %>
            | <% h.link_to('Edit '+c.title, h.url_for(title=c.title, action='edit')) %>
        </p>
        </div>
    </body>
</html>

