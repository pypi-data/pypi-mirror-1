Lineage Proxy Props Tests
=========================

First a little set up::

    >>> import zope.component
    >>> from p4a.subtyper import interfaces
    >>> from Products.CMFCore.interfaces import IPropertiesTool

Let's enable a Child Site.

First we go ahead and register the default engine utility.

    >>> from p4a.subtyper import engine
    >>> zope.component.provideUtility(engine.Subtyper())

Now we can query the engine as we need information.

    >>> subtyper = zope.component.getUtility(interfaces.ISubtyper)

    >>> self.login('contributor')
    >>> _ = self.portal.invokeFactory("Folder", "folder")

At first the simple folder we created has no subtype.

    >>> subtyper.existing_type(self.portal.folder) is None
    True

    >>> subtyper.change_type(self.portal.folder, u'collective.lineage.childsite')
    >>> subtyper.existing_type(self.portal.folder)
    <DescriptorWithName name=collective.lineage.childsite; descriptor=<collective.lineage.descriptors.ChildSiteDescriptor ...>>
    >>> interfaces.ISubtyped.providedBy(self.portal.folder)
    True

Then we test that the subscriber from lineage.proxyprops has done its job and added a ProxyProperties utility to the microsite.

    >>> sm = self.portal.folder.getSiteManager()
    >>> sm.getUtility(IPropertiesTool)
    <collective.proxyproperties.ProxyProperties ...>

