This is QP, a package for defining and running multiple web
applications based on Durus for persistence, standard persistent
Session and User classes, easy interactive database sessions, qpy for
assembling html, and Quixote2-style forms and path traversal.  QP
makes it easier than ever to use these tools together.

QP includes a http/scgi server that dispatches requests to
a pool of long-running single-threaded worker processes.
With QP your applications can
  1) use the QP http service directly,
  2) use the QP http service through a proxy,
  3) use the QP scgi service through Apache+mod_scgi or lighttpd,
  4) use the QP scgi service through CGI, using the (included)
     cgi2scgi adapter and any cgi-capable web server.

QP includes a site-management capability similar to the one in
Dulcinea.  One command line utility (named "qp") is used for 
controlling all of the servers for multiple sites.

QP uses the passfd module from mod_scgi for the servers, and this does
not work on Windows.  QP runs nicely on OS X, Linux, FreeBSD, and probably 
on Solaris.


QUICK START
-----------

Install Python 2.4 or above.

To be as explicit as possible, I'll write the installation procedure here
as if it were a script.

    # Download and unpack the distributions.
    wget http://www.mems-exchange.org/software/files/durus/Durus-3.1.tar.gz
    wget http://www.mems-exchange.org/software/files/qpy/Qpy-1.1.tar.gz
    wget http://www.mems-exchange.org/software/files/qp/QP-1.1.tar.gz
    tar xzf Durus-3.1.tar.gz
    tar xzf qpy-1.1.tar.gz
    tar xzf qp-1.1.tar.gz

    # Install the packages
    cd Durus-3.1; sudo python setup.py install
    cd ../qpy-1.1; sudo python setup.py install # ignore compiler warnings
    cd ../qp-1.1; sudo python setup.py install

    # Make sure that the installed .qpy files are compiled.
    sudo python -c "import qp.fill"

    # Copy the demo sites from the distribution to your ~/qp_sites directory.
    python setup.py install_demo_sites ~/qp_sites

    # Put a symlink to ~/qp_sites in the installed qp package.
    sudo python setup.py install_sites_link ~/qp_sites" 
    

The installation is now complete.

Run the command "qp start".  This will start three demo web servers on:
http://localhost:8000
http://localhost:8001
http://localhost:8002
Look at them in your browser.  Run "qp stop" when you want to stop them.

Run "qp --help" to see the options available for the qp command.


USING QP
--------

Define your sites by editing the qp.sites package, adding a sub-package
for each site you want to run.  The distribution provides three example
sites:  hello, echo, and proto.  A site named 'mine' is expected to
have:
    1) a package named 'mine' in the qp/sites directory.
    2) a 'var' directory in qp/sites/mine for the database and log files.
    3) 'SitePublisher' and 'SiteRootDirectory' classes available for 
       import from qp.sites.mine.

The SitePublisher class should be a subclass of qp.pub.publish.Publisher,
with a 'configuration' class attribute identifying addresses for the
servers you want to run.

The SiteRootDirectoryClass should be a subclass of qp.fill.directory.Directory
that defines your site's content.

Use the 'qp' command to run your sites.  Run 'qp --help' for a full usage
description.


OTHER HELPFUL PACKAGES
----------------------

The qp command has an interaction option that offers an interactive
python session that is connected to the database of one of your sites.
This option doesn't work unless you install Michael Hudson's pyrepl
package, available from http://codespeak.net/pyrepl/.  Once you have
used the interactive features provided by pyrepl, it is hard to live
without them.  The install is very simple: "python setup.py install".

The qp package includes unittests in test subdirectories.  The tests
are written using the very minimalistic testing framework called
Sancho.  If, for some reason, you want to run the unittests, you'll
need to install Sancho-2.1:
http://www.mems-exchange.org/software/sancho/.

If you want to use QP's web service with https, you will probably want
to install either stunnel (http://stunnel.org/) or Apache
(http://apache.org).


HTTPS
-----

QP does *not* provide ssl service, but you can use QP together with
Apache (through SCGI), an ssl-providing proxy, or using stunnel.  The
stunnel method is relatively simple.  You just install stunnel
(available from www.stunnel.org) and configure it to run in server
mode and to accept connections on the public (https_address) interface
and forward them to the port on the local (as_https_address) interface.
The 'echo' site in the distribution, for example, provides the
'as_https' server on localhost port 9001.  If you set stunnel to
accept connections on <yourhost> port 10001 and forward them to
localhost port 9001, then clients can connect to
https://<yourhost>:10001.  


Quick-start stunnel on Debian Linux.
------------------------------------

# The details will be slightly different on Mac OS X or other systems,
# but here are detailed notes for Debian Linux.
apt-get install stunnel4
# "stunnel -version" reports 4.07 as I am testing this.
openssl req -new -x509 -nodes -days 365 \
  -out /etc/stunnel/stunnel.pem -keyout /etc/stunnel/stunnel.pem
# answer the questions.  
chown stunnel4 /etc/stunnel/stunnel.pem
chmod 600 /etc/stunnel/stunnel.pem
# Now /etc/stunnel/stunnel.pem can be used as a default.
# Note that this is unverifiable, and therefore inappropriate
# for many applications.  You may need to get a signed certificate.
# See OpenSSL docs for more information about this.
edit /etc/stunnel/:
Set "cert = /etc/stunnel/stunnel.pem"
Set "client = no"
Comment out debug, output, and all of the lines after
  "; Service-level configuration".
Append the following: """

[hello]
accept = 10000
connect = 9000
TIMEOUTclose = 0

[echo]
accept = 10001
connect = 9001
TIMEOUTclose = 0

[proto]
accept = 10002
connect = 9002
TIMEOUTclose = 0
"""
Edit /etc/default/stunnel4, setting "ENABLED=1". 
Run "/etc/init.d/stunnel4 start"
Now you should be able to load, for example,
https://localhost:10001/


QP
--

The abbreviation "qp" stands for "quantum placet", the Latin phrase
meaning "as much as you please".

Copyright
---------

Copyright (c) 2005 CNRI.