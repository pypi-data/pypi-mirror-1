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

If you know other use case just contact us on mailing list and copy to the author. We will adding it.

You need to customize the main template to remove kss spinner. It will not be done here.

