<%
    links = \
        [   { "name": "Front"
            , "controller": "information"
            , "action": "front"
            }
        ,   { "name": "Repositories"
            ,"controller": "information"
            , "action": "repositories"
            }
        ,   { "name": "Quarantine"
            , "controller": "information"
            , "action": "quarantine"
            }
        ]
%>
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">
<html>
<head>
    <meta http-equiv="content-type" content="text/html; charset=UTF-8">

    <title>Darcs-Server: ${self.title()}</title>

    ${h.javascript_link(h.url_for('/javascripts/sort-table.js'), h.url_for('/javascripts/event-handlers.js'))}
    <script type="text/javascript">
        addEvent(window,"load",function(){setupSortedTables("sortableTable",2);});
    </script>

    ${h.stylesheet_link(h.url_for('/stylesheets/compliant.mako'))}

    <link rel="icon" type="image/x-icon" href="${h.url_for("/images/favicon.ico")}">
</head>
<body>
<div class="container">
    <div class="header">
        <img class="imagefloat" src="${h.url_for("/images/darcs-links-small.png")}" alt="Darcs-server logo">
        <div class="navigation">
            <ul class="navlist">
                ${navlinks(links)}
            </ul>
        </div>
    </div>
    <div class="title">
    </div>
    <div class="content">
        ${next.body()}
        <div class="signature">
            version 0.01.001
        </div>
    </div>
</div>
</body>
</html>

<%def name="navlinks(linkList)">
    % for item in reversed(links):
        % if capture(self.title).lower() == item['name'].lower():
            <li class="current"><a href="${h.url_for(controller=item['controller'], action=item['action'])}">${item['name']}</a></li>
        % else:
            <li><a href="${h.url_for(controller=item['controller'], action=item['action'])}">${item['name']}</a></li>
        % endif
    % endfor
</%def>
