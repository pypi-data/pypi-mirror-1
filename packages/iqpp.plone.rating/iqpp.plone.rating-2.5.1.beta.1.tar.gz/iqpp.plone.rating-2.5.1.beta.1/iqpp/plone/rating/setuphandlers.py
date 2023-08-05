def importVarious(context):
    """Import various settings.
    """
    # Set default permissions
    portal = context.getSite()
    portal.manage_permission("iqpp.plone.rating: view",    ('Manager', 'Member', 'Anonymous'), 1)
    portal.manage_permission('iqpp.plone.rating: rate',    ("Manager", "Member", "Anonymous"), 1)
    portal.manage_permission('iqpp.plone.rating: details', ("Manager", "Member", "Anonymous"), 1)
    portal.manage_permission("iqpp.plone.rating: manage",  ('Manager',), 1)