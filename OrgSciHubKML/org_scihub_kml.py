# -*- coding: utf-8 -*-
"""
/***************************************************************************
 OrgSciHubKML
                                 A QGIS plugin
 Organize SciHub KML in groups
                              -------------------
        begin                : 2017-12-19
        git sha              : $Format:%H$
        copyright            : (C) 2017 by Francesco Paolo Lovergine
        email                : francesco.lovergine@cnr.it
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from PyQt4.QtCore import QSettings, QTranslator, qVersion, QCoreApplication, Qt
from PyQt4.QtGui import QAction, QIcon, QMessageBox, QProgressBar
# Initialize Qt resources from file resources.py
import resources
# Import the code for the dialog
from org_scihub_kml_dialog import OrgSciHubKMLDialog

from osgeo import ogr
from qgis.core import QgsErrorMessage, QgsProject, QgsMapLayerRegistry, QgsVectorLayer
import os.path
import time
import re
import json
import glob

class OrgSciHubKML:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'OrgSciHubKML_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)


        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Org SciHub KML')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'OrgSciHubKML')
        self.toolbar.setObjectName(u'OrgSciHubKML')

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('OrgSciHubKML', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        # Create the dialog (after translation) and keep reference
        self.dlg = OrgSciHubKMLDialog()

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/OrgSciHubKML/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Organize SciHub Downloader KMLs'),
            callback=self.run,
            parent=self.iface.mainWindow())


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&Org SciHub KML'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar

    def err_msg(self, string):
        msg = QMessageBox(self.dlg)
        msg.setText(string)
        msg.setIcon(QMessageBox.Critical)
        msg.show()

    def get_info(self, kml):
        drv = ogr.GetDriverByName("LIBKML")
        ds = drv.Open(kml)
        ly = ds.GetLayer()
        ft = ly.GetFeature(1)
        f = json.loads(ft.ExportToJson())
        p = f['properties']
        sensor = p['PlatformName']
        product = p['ProductType']
        direction = p['OrbitDirection']
        ron = p['RelativeOrbitNumber']
        date = p['BeginDate']
        name = p['Name']
        fields = re.split('[ -]', date)
        year = fields[0]
        month = fields[1]
        return (sensor, product, direction, ron, year, month, name)


    def run(self):
        """Run method that performs all the real work"""
        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            filelist = self.dlg.listOfFilesQgsFileWidget.filePath()
            folder = self.dlg.directoryQgsFileWidget.filePath()
            if not len(filelist) and not len(folder):
                self.err_msg("Please set a list of KML files and/or a repository folder!")
            else:
                self.dlg.close()
                if len(folder) and not os.path.isdir(folder):
                    self.err_msg("Repository folder is not a directory")
                    return
                kmls = []
                if len(filelist):
                    with open(filelist,'r') as fl:
                        content = fl.readlines()
                        content = [l.strip() for l in content] 
                        fl.close()
                    for f in content:
                        if not os.path.isabs(f):
                            path = os.path.join(folder, f)
                        else:
                            path = f
                        extension = os.path.splitext(path)[1][1:]
                        if extension != 'kml':
                            path = os.path.join(path, '.kml')
                        kmls.append(path)
                else:
                    for name in glob.glob(os.path.join(folder,'*.kml')):
                        kmls.append(name)

                groups = {}
                root = QgsProject.instance().layerTreeRoot()
                ogr.UseExceptions()
                monthname = { 1:'jan', 2:'feb', 3:'mar', 4:'apr', 5:'may', 6:'jun', \
                              7:'jul', 8:'aug', 9:'sep', 10:'oct', 11:'nov', \
                              12:'dec', }
                progressMessageBar = self.iface.messageBar().createMessage("Doing something really boring...")
                progress = QProgressBar()
                progress.setMaximum(len(kmls))
                progress.setAlignment(Qt.AlignLeft|Qt.AlignVCenter)
                progressMessageBar.layout().addWidget(progress)
                self.iface.messageBar().pushWidget(progressMessageBar, self.iface.messageBar().INFO)

                main_name = 'SciHub Layers'
                if not root.findGroup(main_name):
                    main = root.addGroup(main_name)
                else:
                    main = root.findGroup(main_name)

                kmls.sort()
                i = 0
                for kml in kmls:
                    (s, p, d, r, y, m, n) = self.get_info(kml)

                    if not main.findGroup(s):
                        sensor = main.addGroup(s)
                    else:
                        sensor = main.findGroup(s)

                    if not sensor.findGroup(p):
                        product = sensor.addGroup(p)
                    else:
                        product = sensor.findGroup(p)

                    if not product.findGroup(d):
                        direction = product.addGroup(d)
                    else:
                        direction = product.findGroup(d)

                    ron_str = "RON:%s" % r
                    if not direction.findGroup(ron_str):
                        ron = direction.addGroup(ron_str)
                    else:
                        ron = direction.findGroup(ron_str)

                    if not ron.findGroup(y):
                        year = ron.addGroup(y)
                        for j in range(1,13):
                            year.addGroup(monthname[j])
                    else:
                        year = ron.findGroup(y)

                    m_str = monthname[int(m)]
                    if not year.findGroup(m_str):
                        month = year.addGroup(m_str)
                    else:
                        month = year.findGroup(m_str)

                    if not QgsMapLayerRegistry.instance().mapLayersByName(n):
                        frame = QgsVectorLayer(kml, n, 'ogr') 
                        QgsMapLayerRegistry.instance().addMapLayer(frame, False)
                        month.addLayer(frame)

                    i += 1
                    progress.setValue(i)

                self.iface.messageBar().clearWidgets()
