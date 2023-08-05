Short package description
=========================

Package developed to provide extended access to object content thru ftp.
Package introduce two considerations:

    1.  All objects are directory;
    
    2.  Object-directory always content one item: attributes
        container. There are over item if object has them.

Full object content can be copied over ftp by means of this technique.
Please, take into considerations: package make attribute values on interface
basis thus values serialized as text and load back as binary.

Package present default adapter set (ng.ftp.default). Current Zope3 ftp
representation can be partial exchanged by ng.ftp package. However, using
special customization each class by means of ftpview zcml-directive is
highly recommended (sorry, this directive is not implemented yet).


Filesystem representations features
-----------------------------------

Directory names
    Directory names use followed format::
        <OBJECT NAME> "=" <OBJECT CLASS NAME>
    
Directory named "++at++"
    content attribute list;
    
FTPWidgets
    There are some FTP-widgets using for values serialization.

Default package customize
-------------------------

To turn on default options subpackage ng,ftp.default are to activate (copy
ng/ftp/etc/ng.ftp.default-configure.zcml to etc/package-includes of zope
instance). Some heuristic adapter set will be activated to provide all
functionality what you need. It's working. But It can break in future. After
that, you can't use usual zope ftp.

Special package customize
-------------------------

My considerations, ftpview zcml-directive is not implemented yet. Let use
default adapter set and be happy.



