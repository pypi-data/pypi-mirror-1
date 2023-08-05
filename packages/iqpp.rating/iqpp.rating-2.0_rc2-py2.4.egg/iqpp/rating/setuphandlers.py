def importVarious(context):
    """Import various settings.
    """
    # Set default permissions
    portal = context.getSite()
    portal.manage_permission('iqpp.rating: rate',    ["Anonymous", "Member"], 1)
    portal.manage_permission('iqpp.rating: details', ["Anonymous", "Member"], 1)
