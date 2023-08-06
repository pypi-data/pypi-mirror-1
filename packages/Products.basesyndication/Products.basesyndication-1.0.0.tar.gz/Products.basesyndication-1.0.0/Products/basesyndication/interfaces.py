from zope.interface import Interface


class IEnclosure(Interface):
    """Represents an 'enclosed' file that is explicitly linked to within
    an IFeedEntry.

    This is here to support podcasting.
    """

    def getURL():
       """URL of the enclosed file.
       """

    def getLength():
       """Return the size/length of the enclosed file.
       """

    def __len__():
       """Synonym for getLength
       """

    def getMajorType():
       """Return the major content-type of the enclosed file.

           e.g. content-type = 'text/plain' would return 'text'.
       """

    def getMinorType():
       """Return the minor content-type of the enclosed file.

           e.g. content-type = 'text/plain' would return 'plain'.
       """

    def getType():
       """Return the content-type of the enclosed file.
       """


class IFeedEntry(Interface):
    """A single syndication feed entry.
    """

    def getWebURL():
        """URL for the web view of this IFeedEntry.
        """

    def getTitle():
        """Title of this entry.
        """

    def getDescription():
        """Description of this entry.
        """

    def getBody():
        """The raw body content of this entry.

        TODO: This needs some thinkwork. RSS accepts all sorts of
        stuff, but Atom is capable of including xhtml without needing
        to resort to CDATA sections and escaping of tags.

        See also getXthml, which should solve this.
        """

    def getXhtml():
        """The (x)html body content of this entry, or None
        """

    def getUID():
        """Unique ID for this entry.

        Especially for the Atom format: this UID should never
        change. Never. This way tools can prevent display of double
        items (like items that are also aggregated into a "planet"
        that you read).
        """

    def getAuthor():
        """Author of this entry.
        """

    def getEffectiveDate():
        """The datetime this entry was first published.
        """

    def getModifiedDate():
        """The datetime this entry was last modified.
        """

    def getTags():
        """The tags/keywords/subjects associated with this entry.

        Return the tags as a list or a tuple, it is up to the actual
        feed to handle the display.
        """

    def getRights():
        """The dublin core 'rights' associated with this entry.
        """

    def getEnclosure():
        """Return an IEnclosure instance or None.
        """


class IFeedSource(Interface):
    """A source of IFeedEntry objects for a feed.
    """

    def getFeedEntries(max_only=True):
        """A sequence of IFeedEntry objects.

        This means the actual objects, not catalog brains or so.
        """
        
    def getMaxEntries():
        """Maximum number of IFeedEntries to show for this feed.
        """

class IFeed(Interface):
    """A syndication feed e.g. RSS, atom, etc.
    """

    def getBaseURL():
        """Used for supporting relative URLs in feeds.
        """

    def getUpdatePeriod():
        """
        """

    def getUpdateFrequency():
        """
        """

    def getImageURL():
        """URL of an image that can be embedded in feeds.
        """

    def getEncoding():
        """Character encoding for the feed.
        """

    def getTitle():
        """Title of this feed.
        """

    def getDescription():
        """Description of the feed.
        """

    # Is this needed? We just want a list of entries to display!
    # That should already be stripped down to size!
    def getMaxEntries():
        """Maximum number of IFeedEntries to show for this feed.

        This is only useful when giving back a number of feed sources
        which you have to filter afterwards.

        When None or 0, just return all entries of all feed sources.
        """

    def getUID():
        """Unique ID for this feed.
        """

    def getWebURL():
        """URL for the web view of this feed.
        """

    # Is this needed? We just want a list of entries to display!
    # If sources have to be queried, why would we do it?
    def getFeedSources():
        """A sequence of IFeedSource objects.
        """

    def getFeedEntries(max_only=True):
        """Return a sequence of IFeedEntry objects with which to build a
        feed.
        """

    # Is this needed? We just want a list of entries to display!
    # That should already be sorted!
    def getSortedFeedEntries(feed_entries=None, max_only=True):
        """Return a sorted sequence of IFeedEntries.  If feed_entries is
        None, call getFeedEntries first.

        Sorting based on publication datetime, newest first.
        """

    def getModifiedDate(max_only=True):
        """The last modified datetime that applies to the whole feed.
        """
