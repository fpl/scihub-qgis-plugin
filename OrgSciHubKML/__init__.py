# -*- coding: utf-8 -*-
"""
/***************************************************************************
 OrgSciHubKML
                                 A QGIS plugin
 Organize SciHub KML in groups
                             -------------------
        begin                : 2017-12-19
        copyright            : (C) 2017 by Francesco Paolo Lovergine
        email                : francesco.lovergine@cnr.it
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load OrgSciHubKML class from file OrgSciHubKML.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .org_scihub_kml import OrgSciHubKML
    return OrgSciHubKML(iface)
