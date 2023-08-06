== Overview ==
addhrefs is a Python module for turning text which has URLs and email
addresses in it into HTML links. The simplest explaination is that it
tries to do what email clients do. If you receive an email written in
plain text with some URLs and email addresses mentioned, they turn
into links that you can open with the web browser.

== About ==
addhrefs is Open Source and free under the ZPL license.
addhrefs was written by Peter Bengtsson, 2004-2006, mail@peterbe.com
(www.peterbe.com) to be used in the IssueTrackerProduct (www.issuetrackerproduct.com)

== Installation ==
Run the setup.py script like any other python package. On Linux:

 $ easy_install addhrefs
 
Alternatively download, unpack and...:

 $ python setup.py build
 $ sudo python setup.py install
 
== Usage ==
 >>> from addhrefs import addhrefs
 >>> print addhrefs("Go to www.peterbe.com")
 Go to <a href="http://www.peterbe.com">www.peterbe.com</a>
 >>> print addhrefs("Contact mail@peterbe.com")
 Contact <a href="mailto:mail@peterbe.com">mail@peterbe.com</a>
 