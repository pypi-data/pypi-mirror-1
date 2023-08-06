.. -*-doctest-*-

================
bbdb.gmailfilter
================

    >>> from bbdb.gmailfilter import export
    >>> export.main(
    ...     ['Foo Name', 'foo@foo.com',
    ...      '2009-06-29,from,bar.group,"Bar & Name" <bar@bar.com>,Qux Name <qux@qux.com>',
    ...      '2009-07-01,to,baz.group,Baz Name <>'])
    <?xml version='1.0' encoding='UTF-8'?>
    <feed xmlns="http://www.w3.org/2005/Atom"
          xmlns:apps="http://schemas.google.com/apps/2006">
      <title>Mail Filters</title>
      <id>tag:mail.google.com,2008:filters:1246258800000,1246431600000</id>
      <updated>...</updated>
      <author>
        <name>Foo Name</name>
        <email>foo@foo.com</email>
      </author>
      <entry>
        <title>Mail Filter</title>
        <id>tag:mail.google.com,2008:filters:1246431600000</id>
        <updated>2009-07-01T00:00:00</updated>
        <content/>
        <apps:property name="to" value="&quot;Baz Name&quot;"/>
        <apps:property name="label" value="baz/group"/>
        <apps:property name="shouldArchive" value="true"/>
      </entry>
      <entry>
        <title>Mail Filter</title>
        <id>tag:mail.google.com,2008:filters:1246258800000</id>
        <updated>2009-06-29T00:00:00</updated>
        <content/>
        <apps:property name="from"
                       value="&quot;bar@bar.com&quot; OR &quot;qux@qux.com&quot;"/>
        <apps:property name="label" value="bar/group"/>
        <apps:property name="shouldArchive" value="true"/>
      </entry>
    </feed>

    