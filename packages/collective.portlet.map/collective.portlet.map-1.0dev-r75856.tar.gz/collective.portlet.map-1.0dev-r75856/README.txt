Introduction
============

  Collective.portlet.map is a GMaps integration product. It leans on the Maps
product, reading Maps configurations, and it uses adapters to extract
geolocalizations.

Using collective.portlet.map you can have a fully functional google map view in
a portlet.

How does it works

  Install collective.portlet.maps and Maps.

  Activate the "Map Portlet" and add one or more Location content in a folder.
The Map Portlet will appear next to the folder view, showing all the Locations
in a handy portlet map.


Note

  Collective.portlet.map overrides the FolderMapView browser view for IATTopic
and IFolder provided by Maps to enable the rendering of the portlet by Maps
javascript code (activated only in maps_map in the original version).
You can remove the new behavior removing the  collective.portlet.map-overrides
directive in the buildout.

