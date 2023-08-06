"""
Sample data setup
-----------------

Let's create a sample container which we can use as our iterable context:

  >>> from zope.app.testing.functional import getRootFolder
  >>> root = getRootFolder()
  >>> cont = Container()

and set a parent for the cont:

  >>> root['cont'] = cont

Now setup some items:

  >>> cont[u'first'] = Content('First', 1)
  >>> cont[u'second'] = Content('Second', 2)
  >>> cont[u'third'] = Content('Third', 3)

  >>> from zope.component import getMultiAdapter
  >>> from zope.publisher.browser import TestRequest
  >>> table_view = getMultiAdapter((cont, TestRequest()), name=u"tableview")
  >>> print table_view()
  <table>
    <thead>
      <tr>
        <th>Name</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td>first</td>
      </tr>
      <tr>
        <td>second</td>
      </tr>
      <tr>
        <td>third</td>
      </tr>
    </tbody>
  </table>


  >>> tvwt = getMultiAdapter((cont, TestRequest()), name=u"tvwt")
  >>> print tvwt()
  <html>
   <body>
    <h1> This is my nice Table renderd in a Templage</h1>
    <table>
    <thead>
      <tr>
        <th>Name</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td>first</td>
      </tr>
      <tr>
        <td>second</td>
      </tr>
      <tr>
        <td>third</td>
      </tr>
    </tbody>
  </table>
   </body>
  </html>

table renderd in a layout with an template

  >>> tpil = getMultiAdapter((cont, TestRequest()), name=u"tablepageinlayout")
  >>> print tpil()
  <html>
   <body>
     <div class="layout"><div>
    <table>
    <thead>
      <tr>
        <th>Name</th>
        <th>Number</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td></td>
        <td></td>
      </tr>
      <tr>
        <td></td>
        <td></td>
      </tr>
      <tr>
        <td></td>
        <td></td>
      </tr>
    </tbody>
  </table>
  </div> 
  </div>
   </body>
  </html>


table renderd in a layout with an render method

  >>> twr = getMultiAdapter((cont, TestRequest()), name=u"tablewithrender")
  >>> print twr()
  <html>
   <body>
     <div class="layout"><table>
    <thead>
      <tr>
        <th>Title</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td>first</td>
      </tr>
      <tr>
        <td>second</td>
      </tr>
      <tr>
        <td>third</td>
      </tr>
    </tbody>
  </table></div>
   </body>
  </html>


"""

import grokcore.view as view 
import grokcore.component as grok

from zope.interface import Interface
from megrok.z3ctable import (ITable, TableView, Column, 
                             GetAttrColumn, NameColumn, TablePage)
from megrok.z3ctable.ftests import Container, Content

from megrok.layout import Layout

class TableView(TableView):
    grok.context(Container)


class Name(NameColumn):
    grok.adapts(None, None, TableView)

#

class TW(TableView):
    grok.name('tvwt')
    grok.context(Container)


class NewName(NameColumn):
    grok.adapts(None, None, TW)

#

class TableLayout(Layout):
    grok.context(Interface)


class TablePageInLayout(TablePage):
    grok.context(Container)


class MyName(GetAttrColumn):
    grok.name('myname')
    grok.adapts(None, None, TablePageInLayout)
    header = u"Name"
    weight = 1 

class MyNumbers(GetAttrColumn):
    grok.name('mynumbers')
    grok.adapts(None, None, TablePageInLayout)
    header = u"Number"
    weight = 2

#

class TableWithRender(TablePage):
    grok.context(Container)


class Title(NameColumn):
    """Display the name of the content item
    """
    grok.adapts(None, None, TableWithRender)
    header = u"Title"



def test_suite():
    from zope.testing import doctest
    from megrok.z3ctable.ftests import FunctionalLayer
    suite = doctest.DocTestSuite(
        optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS
        )
    suite.layer = FunctionalLayer
    return suite 
