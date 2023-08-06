<%inherit file="/information/base.mako"/>
<%def name="title()">Repositories</%def>
<h2>Available Repositories</h2>
<p>
Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec volutpat convallis sem, eget pulvinar purus volutpat at. Proin quis nunc ac enim fringilla placerat vel sed ipsum. Nam egestas mi ut odio pulvinar ultrices in et nulla. Donec venenatis sagittis velit, non feugiat mi egestas in. Pellentesque tempus nisl sed elit hendrerit sit amet eleifend mauris interdum. Praesent varius imperdiet.
</p>
<table class="sortableTable">
    <thead>
        <tr><th>Repository</th><th>Read</th><th>Write</th></tr>
    </thead>
    <tbody>
        % for item in sorted(app_globals.repositories):
            <tr><td>${item}</td><td>${app_globals.readString(item)}</td><td>${app_globals.writeString(item)}</td></tr>
        % endfor
    </tbody>
</table>
