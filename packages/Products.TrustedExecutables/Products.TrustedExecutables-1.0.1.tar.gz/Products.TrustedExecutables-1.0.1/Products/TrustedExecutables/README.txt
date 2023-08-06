TrustedExecutables is a set of executable objects unrestricted
by Zope[2]'s security.
Currently, it contains 'TrustedPageTemplateFile',
'TrustedFSPageTemplate' and 'TrustedFSPythonScript'.
'TrustedFSPageTemplate' and 'TrustedFSPythonScript' are registered
with the filename extensions 'xpt' and 'xpy', respectively.

As Zope's security checks are expensive, avoiding them can
drastically speed things up.

On the other hand, these objects must make their own security
checks at places where access control is required.

Use with extreme care!


ATTENTION: Use this version only with Zope 2.11 or above.
Versions for Zope 2.7 upto Zope 2.9 can be found on
http://www.dieter.handshake.de/pyprojects/zope

ATTENTION: It is not unlikely that this product breaks between
Zope releases, as it uses undocumented implementation artefacts.
It is probably not very difficult to fix things again but
you will need programming skills to do so.
