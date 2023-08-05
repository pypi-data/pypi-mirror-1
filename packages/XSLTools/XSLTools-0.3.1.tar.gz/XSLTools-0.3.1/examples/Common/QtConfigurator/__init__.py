#!/usr/bin/env python

"An example of a system configurator which runs under PyQt and WebStack."

import os

class ConfiguratorResource:

    # Standard attributes.

    resource_dir = os.path.join(os.path.split(__file__)[0], "Resources")

    design_resources = {
        "configuration" : "config.ui"
        }

    widget_resources = {
        "hard_disk" : ("config_hard_disk.ui", "hard_disk"),
        "memory_unit" : ("config_memory_unit.ui", "memory_unit"),
        "storage_unit" : ("config_storage_unit.ui", "storage_unit")
        #"hard_disks" : ("config_hard_disks.ui", "hard_disks"),
        #"memory_units" : ("config_memory_units.ui", "memory_units"),
        #"storage_units" : ("config_storage_units.ui", "storage_units")
        }

    document_resources = {
        "base-system" : "config_base_system.xml",
        "cpu" : "config_cpu.xml",
        "hard-disk" : "config_hard_disk.xml",
        "keyboard" : "config_keyboard.xml",
        "memory-unit" : "config_memory_unit.xml",
        "mouse" : "config_mouse.xml",
        "screen" : "config_screen.xml",
        "storage-unit" : "config_storage_unit.xml"
        }

    # Initialisation.

    def __init__(self, *args, **kw):
        pass

    def form_init(self):

        self.reset_collection(self.child("hard_disks"))
        self.reset_collection(self.child("memory_units"))
        self.reset_collection(self.child("storage_units"))

    def form_populate(self):

        # Get field data.
        # NOTE: This would be done for whole page updates in a Web application.

        self.populate_list(self.child("base_system"), self.get_elements("base-system"))
        self.populate_list(self.child("keyboard"), self.get_elements("keyboard"))
        self.populate_list(self.child("mouse"), self.get_elements("mouse"))
        self.populate_list(self.child("screen"), self.get_elements("screen"))

    # General functionality.

    def form_refresh(self, current_text=None):

        # Ensure consistency.
        # NOTE: This would be done for whole page updates in a Web application.
        # NOTE: This would also be done for page updates where the information
        # NOTE: involved was important.

        current_text = current_text or self.child("base_system").currentText()

        # Find the CPU socket and the interface of the current base system.
        cpu_socket = None
        interface = None
        for element in self.get_elements("base-system"):
            text = element.getAttribute("value")
            if text == current_text:
                cpu_socket = element.getAttribute("cpu-socket")
                interface = element.getAttribute("interface")

        # Find all valid CPUs.
        valid = []
        for element in self.get_elements("cpu"):
            if not element.hasAttribute("cpu-socket") or element.getAttribute("cpu-socket") == cpu_socket:
                valid.append(element)
        self.populate_list(self.child("cpu"), valid)

        # Find all valid hard disks.
        valid = []
        for element in self.get_elements("hard-disk"):
            if not element.hasAttribute("interface") or element.getAttribute("interface") == interface:
                valid.append(element)
        for hard_disk_value in self.factory.find_widgets(self, "hard_disk_value"):
            self.populate_list(hard_disk_value, valid)

        # Find memory units.
        for memory_unit_value in self.factory.find_widgets(self, "memory_unit_value"):
            self.populate_list(memory_unit_value, self.get_elements("memory-unit"))

        # Find storage units.
        for storage_unit_value in self.factory.find_widgets(self, "storage_unit_value"):
            self.populate_list(storage_unit_value, self.get_elements("storage-unit"))

    # Slots.

    def baseSystemChanged(self, current_text):
        self.request_refresh(current_text)

    def addHardDisk(self):
        #hard_disks = self.prepare_widget("configuration", "hard_disks")
        #tab_pages = hard_disks.child("tab pages")
        #tab = tab_pages.child("tab")
        #self.child("hard_disks").addTab(tab, hard_disks.tabLabel(tab))
        #self.factory.connect(tab, self)
        hard_disk = self.prepare_widget("configuration", "hard_disk", self.child("hard_disks"))
        self.child("hard_disks").layout().add(hard_disk)
        hard_disk.show()
        self.factory.connect(hard_disk, self)

        # Perform the consistency check.
        # NOTE: This is not as efficient as it could be since the general check
        # NOTE: refreshes all fields, not just newly added ones.
        self.request_refresh()

    def addMemoryUnit(self):
        #memory_units = self.prepare_widget("configuration", "memory_units")
        #tab_pages = memory_units.child("tab pages")
        #tab = tab_pages.child("tab")
        #self.child("memory_units").addTab(tab, memory_units.tabLabel(tab))
        #self.factory.connect(tab, self)
        memory_unit = self.prepare_widget("configuration", "memory_unit", self.child("memory_units"))
        self.child("memory_units").layout().add(memory_unit)
        memory_unit.show()
        self.factory.connect(memory_unit, self)

        # Perform the consistency check.
        # NOTE: This is not as efficient as it could be since the general check
        # NOTE: refreshes all fields, not just newly added ones.
        self.request_refresh()

    def addStorageUnit(self):
        #storage_units = self.prepare_widget("configuration", "storage_units")
        #tab_pages = storage_units.child("tab pages")
        #tab = tab_pages.child("tab")
        #self.child("storage_units").addTab(tab, storage_units.tabLabel(tab))
        #self.factory.connect(tab, self)
        storage_unit = self.prepare_widget("configuration", "storage_unit", self.child("storage_units"))
        self.child("storage_units").layout().add(storage_unit)
        storage_unit.show()
        self.factory.connect(storage_unit, self)

        # Perform the consistency check.
        # NOTE: This is not as efficient as it could be since the general check
        # NOTE: refreshes all fields, not just newly added ones.
        self.request_refresh()

    def removeHardDisk(self):
        #page = self.hard_disks.currentPage()
        #self.hard_disks.removePage(page)
        #page.deleteLater()
        remove_hard_disk = self.sender()
        hard_disk = remove_hard_disk.parent()
        self.child("hard_disks").layout().remove(hard_disk)
        hard_disk.deleteLater()

    def removeMemoryUnit(self):
        #page = self.memory_units.currentPage()
        #self.memory_units.removePage(page)
        #page.deleteLater()
        remove_memory_unit = self.sender()
        memory_unit = remove_memory_unit.parent()
        self.child("memory_units").layout().remove(memory_unit)
        memory_unit.deleteLater()

    def removeStorageUnit(self):
        #page = self.storage_units.currentPage()
        #self.storage_units.removePage(page)
        #page.deleteLater()
        remove_storage_unit = self.sender()
        storage_unit = remove_storage_unit.parent()
        self.child("storage_units").layout().remove(storage_unit)
        storage_unit.deleteLater()

    def updateConfig(self):
        self.form_refresh()

    def exportConfig(self):
        print "configuration.exportConfig(): Not implemented yet"

def get_resource(resource_type, *args, **kw):

    if resource_type == "PyQt":
        import XSLForms.Resources.PyQtResources
        try:
            import QtConfigurator.Forms
        except ImportError:
            print "*" * 60
            print "Please generate the following file before running this example:"
            print os.path.join(os.path.split(__file__)[0], "Forms.py")
            print "Use the pyuic program along with the form definition file:"
            print os.path.join(os.path.split(__file__)[0], "Resources", "config.ui")
            print "*" * 60
            print
            raise
        class Configurator(ConfiguratorResource, QtConfigurator.Forms.Configurator, XSLForms.Resources.PyQtResources.XSLFormsResource):
            def __init__(self, *args, **kw):
                QtConfigurator.Forms.Configurator.__init__(self, *args, **kw)
                XSLForms.Resources.PyQtResources.XSLFormsResource.__init__(self, "configuration")
                ConfiguratorResource.__init__(self, *args, **kw)
        resource = Configurator(*args, **kw)
        resource.form_init()
        resource.form_populate()

    else:
        import XSLForms.Resources.PyQtWebResources
        from WebStack.Resources.ResourceMap import MapResource
        from WebStack.Resources.Static import DirectoryResource

        class Configurator(ConfiguratorResource, XSLForms.Resources.PyQtWebResources.XSLFormsResource):
            def __init__(self, *args, **kw):
                XSLForms.Resources.PyQtWebResources.XSLFormsResource.__init__(self, "configuration")
                ConfiguratorResource.__init__(self, *args, **kw)

        configurator_resource = Configurator(*args, **kw)
        directory = configurator_resource.resource_dir
        resource = MapResource({
            "styles" : DirectoryResource(os.path.join(directory, "styles"), {"css" : "text/css"}),
            "scripts" : DirectoryResource(os.path.join(directory, "scripts"), {"js" : "text/javascript"}),
            "" : configurator_resource
            })

        # Do not initialise or populate the resource here: both happen when a
        # Web request is received (initialisation when no form document is
        # found; population when a form document is prepared for output).

    return resource

# vim: tabstop=4 expandtab shiftwidth=4
