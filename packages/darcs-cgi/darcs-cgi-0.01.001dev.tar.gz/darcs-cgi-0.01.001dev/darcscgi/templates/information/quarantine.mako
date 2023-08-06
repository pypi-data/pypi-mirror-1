<%inherit file="/information/base.mako"/>
<%def name="title()">Quarantine</%def>
<h2>The Quarantine</h2>
<p>
Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec volutpat convallis sem, eget pulvinar purus volutpat at. Proin quis nunc ac enim fringilla placerat vel sed ipsum. Nam egestas mi ut odio pulvinar ultrices in et nulla. Donec venenatis sagittis velit, non feugiat mi egestas in. Pellentesque tempus nisl sed elit hendrerit sit amet eleifend mauris interdum. Praesent varius imperdiet.
</p>
<table class="sortableTable">
    <thead>
        <tr><th>Patches</th><th>Size</th><th>Container</th></tr>
    </thead>
    <tbody>
        % if not c.quarantinedFiles:
            <tr><td colspan="3">**No Patches**</td></tr>
        % else:
        % for item in c.quarantinedFiles:
            <tr><td>${item[0]}</td><td>${str(item[1] / 1024)[:4]}kB</td><td>${item[2]}</td></tr>
        % endfor
        % endif
    </tbody>
</table>
