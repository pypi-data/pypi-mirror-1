The zcmljunction is zope3 product developed to provide possibility rapid
interface adapter creation. To create adapter you can use new junction
zcml-directive. Adapter can provide output interface attributes from
attributes of input interface or it join.

Sample of use::

  <junction
    for=".interfaces.IArticle"
    provides=".interfaces.ISearch"
    factory = ".searchadapter.SearchAdapter"
    >
    <property in="title" out="title"/>
    <property in="abstract" out="abstract"/>
    <property in="body" out="body" default=""/>
    <property in="abstract klass name keyword title body author" out="common" default=""/>
  </junction>

