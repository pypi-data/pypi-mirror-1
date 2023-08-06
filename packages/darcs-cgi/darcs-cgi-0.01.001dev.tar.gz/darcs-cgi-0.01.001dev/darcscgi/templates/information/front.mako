<%inherit file="/information/base.mako"/>
<%def name="title()">Front</%def>
<h2>About</h2>
<p>
Darcs-links extends the darcs distributed revision control system by facilitating authenticated gets and sends to and from remote repositories. Access is authorized via OpenPGP keyrings, and pushes can additionally be encrypted. Unauthorized pushes can be redirected to quarantine zones. Furthermore, darcs-links provides a web interface summarizing available repositories and quarantined files.
</p>
<p>
Darcs-links is not a web interface that allows code browsing. For such functionality, use darcsweb, redmine or tracs.
</p>
<h2>Server-Side</h2>
<p>
Darcs-links runs on top of the pylons web framework. As such, it needs a WSGI capable webserver. This is available to apache through mod_wsgi. Lighttpd can also run WSGI applications.
</p>
<p>
Darcs-links needs to have write-access to the quarantine location. Repositories also need sufficient permissions, however darcs-links does not attempt to write to read-only repositories.
</p>
<p>
First configure the pylons preferences file to point to the repository configuration file. Then the application can be loaded into a webserver. The following script configures the application&#39;s site-directories for virtual environments under mod_wsgi.
</p>
<pre>
import sys,site

ALLDIRS = ['/virtualenv/lib/python2.x/site-packages']

# Remember original sys.path.
prev_sys_path = list(sys.path)

# Add each new site-packages directory.
for directory in ALLDIRS:
  site.addsitedir(directory)

# Reorder sys.path so new directories at the front.
new_sys_path = []
for item in list(sys.path):
    if item not in prev_sys_path:
        new_sys_path.append(item)
        sys.path.remove(item)
sys.path[:0] = new_sys_path

from paste.deploy import loadapp

application = loadapp('config:/path/to/darcs-links/deployment.ini')
</pre>
<p>
<cite>[*] see the <a href="http://code.google.com/p/modwsgi/wiki/VirtualEnvironments">modwsgi virtualenv page</a> for more details.</cite>
</p>
<p>
An example configuration: <a href="${h.url_for("/static/example-configuration.xml")}">example-configuration.xml</a>.
</p>
<p>
An equivalent to the internal defaults: <a href="${h.url_for("/static/default-configuration.xml")}">default-configuration.xml</a>.
</p>
<h2>Client-Side Download</h2>
<p>
When read-authentication is enabled, darcs-links expects to receive an authentication string in the body of the POST. This is simply an OpenPGP clearsigned and ascii armored message that contains one line: "welcome". To create the signature.
</p>
<pre>
echo "welcome">filename
gpg --clearsign --armor filename
</pre>
<p>
Then instruct whichever http client darcs uses to send the authentication string.
</p>
<pre>
export DARCS_GET_HTTPS="curl -3 -k --data-urlencode sig@/path/to/file.asc"
</pre>
<p>
Darcs-links first verifies the contents of the message, then checks that the signature matches the contents and the the signature is allowed in accordance to the repository keyring.
</p>
<h2>Client-Side Uploads</h2>
<p>
Darcs can create an rfc822 formatted (email) message from a patch bundle to send via HTTP POST as follows.
</p>
<pre>
darcs send --sign --to http://url
</pre>
<p>
Unfortunately darcs is only able to send the patch bundle via HTTP. To enable HTTPS or other protocols, darcs must employ an external program called from the DARCS_APPLY_FOO environment variable.
<p>
<pre>
export DARCS_APPLY_HTTPS="curl -3 -k --data-urlencode @-"
darcs push --sign
</pre>
<h2>License</h2
<p>
Software components permitting, I would like to release this software under the GPLv3.
<p>
