Short package description
=========================

Package developed to provide possibility xmlrpc server tree and edit
attributes of some interfaces by external applicaton.

Package provide utility:

    ngxmlrpcscan

        The ngxmlrpcscan  developed to scan xmlrpc server tree and print or
        edit attributes of some interfaces by external applicaton

        Used::

            ngxmlrpcscan [<Switches>] <URL> [<ATTRIBUTE>  ...]

        Switches:

            -v
                Be verbose;

            -p
                Do pause each time when exteranl routin run;

            -c
                Check class

            -s
                Atribut are to save after external routin run;

            -c <CLASSNAME>
                Object checked on condition: "is object of this class".

            -i <INTERFACE>
                Adapt object to this interface;

            -n
                Pointed object used without any scan by tree

            -e
                External routin used (do print otherwize), filename will be
                substituted indeed substring %(name)s in this string. It
                supposed running program read filename when started and
                write after finish;



        Arguments::

            <URL>
                Scan tree will be begun on this URL. For authorization,
                you must insert login and pasword into URL. Let see
                sample bellow;
                
            <ATTRIBUTE>
                Any attribute acceptable via interface bellow.
        
Sample
------

Please, issued command::

    ngxmlrpcscan.py -s -p -v \
        -i zope.app.folder.folder.Folder
        -с zope.dublincore.interfaces.IZopeDublinCore \
        -e "joe  %(name)s "
        http://theman:12345678@localhost:8080/Root/Main \
         title description        
       
The ngxmlrpcscan scaned object tree rooted in
http://theman:12345678@localhost:8080/Root/Main to find all folders and to
edit folder methadata via IZopeDublinCore adapter.

You can edit one object attribute with command::

    ngxmlrpcscan -v  -e -n \
        http://theman:12345678@localhost:8080/Root/Main \
        "joe '%(name)s'" body 
    
Just enter and enjoy!

        
