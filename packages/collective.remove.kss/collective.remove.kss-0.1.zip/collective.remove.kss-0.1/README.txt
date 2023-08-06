Introduction
============

This collective module remove KSS from a base Plone install. So you decrease the weight of a Page. It has been done for testing purpose.

You have to know that removing KSS remove also some Plone features:

   * inline editing
   * inline validation
   * lock on edit (parts of it, anyway)
   * auto-refreshing of portlets with a kssPortletRefresh class
   * some of the action menu stuff (e.g. AJAX changing of workflow state)
   * navigation of the calendar portlet to different months

If you know other use case just contact us one Mailing List and copy to the author. We will adding it.

At the moment the uninstall is not supported throw the quickinstaller (Plone UI) but you can use portal_setup and apply the uninstall profile that just re install kss.

CMFQuickInstall need a patch to support uninstall profile from eggs.

