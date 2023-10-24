from steps.constantfiles.constants import * # NOSONAR
# Inventory_Class
# EndPoints
INV_DEVICES_ID = "/inventory/devices/{}"
INV_DEVICES_ID_TYPE = INV_DEVICES_ID + "?search=type=='{}'"
INV_DEVICES_ID_RAW = INV_DEVICES_ID + "/raw"
INV_DEVICES_ID_CHANGES = INV_DEVICES_ID + "/changes"
INV_DEVICES_ID_TIMESTAMPS = INV_DEVICES_ID + "/reportTimestamps"
INV_DEVICES_ID_SNAPSHOT = INV_DEVICES_ID + "/snapshots/{}"
INV_DEVICES_ID_ASSIGNMENTS = "/remote-flashing/core/devices/{}/assignments"
VEHICLE_INVENTORY_JSON_PATH = "common\\TestData\\FleetManagement\\vehicle_inventory.json"