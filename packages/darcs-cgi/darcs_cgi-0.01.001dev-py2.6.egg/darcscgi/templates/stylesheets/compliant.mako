<%text>
html, body {
    position: relative;
    height: 100%;
    margin: 0em;
    padding: 0em;
    background-color: rgb(230,230,230);
    font-family: verdana, sans-serif, monospace;
    font-size: 1.0em;
    font-weight: 400;
    font-style: normal;
    text-align: left;
}

a:link { color: rgb(0,0,100); text-decoration:none; }
a:visited { color: rgb(100,100,100); text-decoration:none; }
a:hover { color: rgb(100,150,50); text-decoration:underline; }
a:focus { color: rgb(130,255,0); text-decoration:underline; }

h2 {
    font-size: 1.4em;
    font-weight: 800;
    margin: 0.75em 0em 0.5em 0em;
}

.container {
    width: 50em;
    min-height:100%;
    margin: 0em auto 0em auto;
    background-color: rgb(210,210,210);
    overflow: auto;
}

.header {
    position: relative;
    height: 9em;
    background-color: rgb(100,100,100);
}

.imagefloat {
    float: left;
    height: 80px;
    margin: 0.5em 0em 0em 0.5em;
}

.navigation {
    position: absolute;
    bottom: 0;
    right: 0;
}

.navlist {
    font-weight: 900;
}

.navlist li {
    display: inline;
    list-style: none;
}

.navlist li a {
    float: right;
    min-width: 6em;
    padding: 1em 1em 2em 1em;
    margin: 0em 1em 0em 0em;
    border: 0.5em solid rgb(150,150,140);
    border-bottom: none;
    background: rgb(210,210,210);
    text-decoration: none;
    text-align: center;
}

.navlist li a:link {
    color: rgb(0,0,100);
}

.navlist li a:visited {
    color: rgb(50,50,100); 
}

.navlist li a:hover {
    color: rgb(0,0,0);
    border-color: rgb(50,50,50);
    background-color: rgb(180,220,170);
}

.navlist li.current a:hover {
    color: rgb(0,0,0);
    border-color: rgb(50,50,50);
    background-color: rgb(180,220,170);
}

.navlist li.current a {
    border-color: rgb(50,50,50);
    background-color: rgb(210,210,210);
}

.title {
    display: none;
    width: 30%;
    margin: 1em auto 0.5em auto;
    padding: 0.5em 2em 0.5em 2em;
    background-color: rgb(220,180,150);
    font-size: 1.75em;
    font-weight: 600;
    text-align: center;
}

.content {
    margin: 3em 5em 3em 5em;
    padding: 0.5em 0.5em 0.5em 0.5em;
    background-color: rgb(200,250,170);
}

.signature {
    width: 90%;
    margin: 1.5em auto 0.25em auto;
    padding: 0.25em 0.5em 0em 0.5em;
    border-top: 0.2em groove rgb(50,50,50);
    text-align: right;
}

pre {
    margin: 1em 3em 1em 3em;
    padding: 0.5em 0.75em 0.5em 0.75em;
    border: 0.2em dotted rgb(170,170,170);
    background-color: rgb(210,210,210);
    overflow: hidden;
    white-space: pre-wrap;
    text-wrap: suppress;
    word-wrap: break-word;
}

cite {
    font-family: monospace;
}

.bold {
    font-weight: 800;
}

/* default table CSS */
table {
    margin: 0.5em auto 0.5em auto;
    border: 0.4em rgb(50,50,100) solid;
    border-collapse: separate;
    border-spacing: 0.15em;
    padding: 0.4em;
    background-color: rgb(230,230,230);
}

th {
    padding: 0.1em 1.0em 0.1em 1.0em;
    text-align: center;
    white-space: nowrap;
}

tr {
    background-color: rgb(210,210,210);
}

td {
    width: 4em;
    min-width: 4em;
    padding: 0.3em 1.0em 0.3em 1.0em;
    text-align: center;
    white-space: nowrap;
}
</%text>
