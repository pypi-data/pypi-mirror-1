.. -*-doctest-*-

===================
collective.nextprev
===================

The collective.nextprev package extends Plone's next/previous
navigation for folders to collections (AKA topics or smart folders).
If a listing view is visited for a collection which has next/previous
navigation enabled, a cookie is set to remember the collection used
and any relevant query terms.  When a content item in the result set
is visited, this cookie will be used to determine the next and
previous item links.

Start with the a folder, some content, and a collection.

    >>> folder
    <ATFolder at /plone/Members/test_user_1_>
    >>> folder.contentValues()
    [<ATTopic at /plone/Members/test_user_1_/foo-topic-title>,
     <ATNewsItem at /plone/Members/test_user_1_/foo-news-item-title>,
     <ATDocument at /plone/Members/test_user_1_/bar-page-title>,
     <ATNewsItem at /plone/Members/test_user_1_/baz-news-item-title>,
     <ATNewsItem at
      /plone/Members/test_user_1_/qux-baz-news-item-title>]

One item is a page and so doesn't show up in the collection listing.

    >>> folder['foo-topic-title'].queryCatalog(full_objects=True)
    [<ATNewsItem at /plone/Members/test_user_1_/foo-news-item-title>,
     <ATNewsItem at /plone/Members/test_user_1_/baz-news-item-title>,
     <ATNewsItem at
      /plone/Members/test_user_1_/qux-baz-news-item-title>] 

Next/previous navigation is enabled for the folder but not for the topic.

    >>> folder.getNextPreviousEnabled()
    True
    >>> folder['foo-topic-title'].getNextPreviousEnabled()
    False

Open a browser at the folder.

    >>> from Products.Five.testbrowser import Browser
    >>> browser = Browser()
    >>> browser.handleErrors = False
    >>> browser.open(folder.absolute_url())

Visit one of the news items, the next link points to the next item in
the folder but not the next item in the collection.

    >>> browser.getLink('Foo News Item Title').click()
    >>> browser.getLink('Next')
    <Link text='Next: Bar Page Title Right arrow[IMG]'
    url='http://nohost/plone/Members/test_user_1_/bar-page-title'>

Open a browser, log in as some one who can enable the next/previous
navigation for the collection, and do so.

    >>> from Products.PloneTestCase import ptc
    >>> owner_browser = Browser()
    >>> owner_browser.handleErrors = False
    >>> owner_browser.open(folder['foo-topic-title'].absolute_url())
    >>> owner_browser.getLink('Log in').click()
    >>> owner_browser.getControl(
    ...     'Login Name').value = ptc.portal_owner
    >>> owner_browser.getControl(
    ...     'Password').value = ptc.default_password
    >>> owner_browser.getControl('Log in').click()
    >>> owner_browser.getLink('Edit').click()
    >>> owner_browser.getControl(
    ...     'Enable next previous navigation').selected = True
    >>> owner_browser.getControl('Save').click()
    >>> print owner_browser.contents
    <...
    ...Changes saved...

Now that next/previous navigation is enabled, visiting the collection
listing will set the cookie.

    >>> browser.open(folder.absolute_url())
    >>> browser.headers['set-cookie']
    'nextprev.collection="/plone/Members/test_user_1_/foo-topic-title";
    Path=/, nextprev.form="test="; Path=/'

Visit an item again and now the next link will be the next item in the
collection.

    >>> browser.getLink('Foo News Item Title').click()
    >>> browser.getLink('Next')
    <Link text='Next: Baz News Item Title Right arrow[IMG]'
    url='http://nohost/plone/Members/test_user_1_/baz-news-item-title'>

If the folder listing is visited again, the next/previous links
reflect the folder contents instead of the collection results.

    >>> browser.open(folder.absolute_url()+'/folder_listing')
    >>> browser.headers['set-cookie']
    'nextprev.collection="deleted"; Path=/; Expires=Wed,
    31-Dec-97 23:59:59 GMT; Max-Age=0, nextprev.form="deleted";
    Path=/; Expires=Wed, 31-Dec-97 23:59:59 GMT; Max-Age=0'

    >>> browser.getLink('Foo News Item Title').click()
    >>> browser.getLink('Next')
    <Link text='Next: Bar Page Title Right arrow[IMG]'
    url='http://nohost/plone/Members/test_user_1_/bar-page-title'>

Search criteria submitted in the request are also preserved in the
cookies so that the next/previous links will reflect the correct
result sets.

    >>> browser.open(folder.absolute_url()+'?SearchableText=baz')
    >>> browser.getLink('Baz News Item Title').click()
    >>> browser.getLink('Previous')
    Traceback (most recent call last):
    LinkNotFoundError
    >>> browser.getLink('Next')
    <Link text='Next: Qux Baz News Item Title Right arrow[IMG]'
    url='http://nohost/plone/Members/test_user_1_/qux-baz-news-item-title'>
