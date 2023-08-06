Who wrote it?
-------------

Tim Hicks - tim@sitefusion.co.uk


What is it?
-----------

fatsyndication is a library that provides implementations for the
interfaces (and templates) defined in basesyndication.  These
implementations take the form of adapters.  Base/mixin adapters are
provided for each of IFeed, IFeedSource and IFeedEntry, but you will
probably need to subclass and override some methods to take account of
the interface(s) that you are adapting from.  An example of this can
be seen in fatsyndication.adapters.feedentry.DocumentFeedEntry.


How do I use it?
----------------

The basic design is this:

1) Declare adapters to IFeedEntry from those interfaces that you want
   to appear in your syndication feeds;

2) Declare adapters to IFeedSource from those (probably container-ish)
   interfaces that you wish to supply IFeedEntry instances to an
   IFeed.  This is a very simple interface to implement.

3) Declare adapters to IFeed from those interfaces that you wish to
   have syndication feeds for.

4) Declare browser:page(s) (in ZCML) for your IFeed-adaptable
   interfaces that use the fatsyndication.browser.feed.GenericFeedView
   view class.

This should give you syndication feeds :).

For an example, see syndication.py and syndication.zcml from the
Quills product (also in the Collective).


Why 'FAT'?
----------

'F' for Five, 'AT' for Archetypes.
