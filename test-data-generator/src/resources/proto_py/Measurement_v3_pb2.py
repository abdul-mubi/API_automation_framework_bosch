# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: Measurement_v3.proto
"""Generated protocol buffer code."""
from google.protobuf.internal import enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x14Measurement_v3.proto\x12\x14RemoteMeasurement_v3\"\x8f\x01\n\x0bMeasurement\x12\x19\n\x0eVERSION_SCHEMA\x18\x01 \x01(\x03:\x01\x33\x12\x37\n\x0cseries_group\x18\x02 \x03(\x0b\x32!.RemoteMeasurement_v3.SeriesGroup\x12,\n\x06marker\x18\x03 \x03(\x0b\x32\x1c.RemoteMeasurement_v3.Marker\"\x8a\x01\n\x06Marker\x12\x11\n\ttimestamp\x18\x01 \x02(\x12\x12\r\n\x05label\x18\x02 \x02(\t\x12.\n\x04type\x18\x03 \x02(\x0e\x32 .RemoteMeasurement_v3.MarkerType\x12.\n\x04\x64\x61ta\x18\x04 \x03(\x0b\x32 .RemoteMeasurement_v3.MarkerData\")\n\nMarkerData\x12\x0c\n\x04name\x18\x01 \x02(\t\x12\r\n\x05value\x18\x02 \x02(\t\"p\n\x0bSeriesGroup\x12,\n\x06series\x18\x01 \x03(\x0b\x32\x1c.RemoteMeasurement_v3.Series\x12\x33\n\ntime_point\x18\x02 \x03(\x0b\x32\x1f.RemoteMeasurement_v3.TimePoint\"e\n\x06Series\x12\x0b\n\x03key\x18\x01 \x02(\r\x12\x0c\n\x04name\x18\x02 \x02(\t\x12\x33\n\nvalue_type\x18\x03 \x02(\x0e\x32\x1f.RemoteMeasurement_v3.ValueType\x12\x0b\n\x03uid\x18\x04 \x02(\t\"S\n\tTimePoint\x12\x11\n\ttimestamp\x18\x01 \x02(\x12\x12\x33\n\ndata_point\x18\x02 \x03(\x0b\x32\x1f.RemoteMeasurement_v3.DataPoint\"K\n\tDataPoint\x12\x12\n\nseries_ref\x18\x01 \x02(\r\x12*\n\x05value\x18\x02 \x02(\x0b\x32\x1b.RemoteMeasurement_v3.Value\"\xf5\x01\n\x05Value\x12\x37\n\x0cscalar_value\x18\x01 \x01(\x0b\x32!.RemoteMeasurement_v3.ScalarValue\x12\x34\n\rgpsdata_value\x18\x02 \x01(\x0b\x32\x1d.RemoteMeasurement_v3.GPSData\x12\x34\n\nlist_value\x18\x03 \x01(\x0b\x32 .RemoteMeasurement_v3.ScalarList\x12G\n\x17\x63lassification_nd_value\x18\x04 \x01(\x0b\x32&.RemoteMeasurement_v3.ClassificationND\"\x85\x01\n\x0bScalarValue\x12\x12\n\nbool_value\x18\x01 \x01(\x08\x12\x13\n\x0b\x62ytes_value\x18\x02 \x01(\x0c\x12\x37\n\x0cnumber_value\x18\x03 \x01(\x0b\x32!.RemoteMeasurement_v3.NumberValue\x12\x14\n\x0cstring_value\x18\x04 \x01(\t\"9\n\x0bNumberValue\x12\x14\n\x0c\x64ouble_value\x18\x01 \x01(\x01\x12\x14\n\x0csint64_value\x18\x02 \x01(\x12\"\x94\x01\n\x07GPSData\x12\x11\n\tlongitude\x18\x01 \x02(\x01\x12\x10\n\x08latitude\x18\x02 \x02(\x01\x12\x11\n\televation\x18\x03 \x01(\x01\x12\x10\n\x08gps_time\x18\x04 \x01(\x04\x12\x11\n\tdirection\x18\x05 \x01(\x01\x12\x11\n\tgps_speed\x18\x06 \x01(\x01\x12\x19\n\x11last_reading_time\x18\x07 \x01(\x12\">\n\nScalarList\x12\x30\n\x05value\x18\x01 \x03(\x0b\x32!.RemoteMeasurement_v3.ScalarValue\"\x80\x01\n\x10\x43lassificationND\x12\t\n\x01n\x18\x01 \x02(\r\x12\x37\n\x05value\x18\x02 \x03(\x0b\x32(.RemoteMeasurement_v3.ClassificationList\x12(\n\x04\x61xis\x18\x03 \x03(\x0b\x32\x1a.RemoteMeasurement_v3.Axis\"N\n\x12\x43lassificationList\x12\x38\n\x05value\x18\x01 \x03(\x0b\x32).RemoteMeasurement_v3.ClassificationValue\"\x96\x01\n\x13\x43lassificationValue\x12\x37\n\x0cnumber_value\x18\x01 \x01(\x0b\x32!.RemoteMeasurement_v3.NumberValue\x12\x46\n\x14\x63lassification_value\x18\x02 \x01(\x0b\x32(.RemoteMeasurement_v3.ClassificationList\"\xc2\x01\n\x04\x41xis\x12\x12\n\nstart_time\x18\x01 \x02(\x12\x12\x10\n\x08\x65nd_time\x18\x02 \x02(\x12\x12\x34\n\rstart_gpsdata\x18\x03 \x01(\x0b\x32\x1d.RemoteMeasurement_v3.GPSData\x12\x32\n\x0b\x65nd_gpsdata\x18\x04 \x01(\x0b\x32\x1d.RemoteMeasurement_v3.GPSData\x12\x15\n\rstart_mileage\x18\x05 \x01(\x04\x12\x13\n\x0b\x65nd_mileage\x18\x06 \x01(\x04*\x9e\x01\n\nMarkerType\x12\x11\n\rSTART_TRIGGER\x10\x00\x12\x10\n\x0cSTOP_TRIGGER\x10\x01\x12\x15\n\x11\x44RIVE_CYCLE_START\x10\x02\x12\x13\n\x0f\x44RIVE_CYCLE_END\x10\x03\x12\x11\n\rGENERIC_EVENT\x10\x04\x12\x14\n\x10JOB_INSTALLATION\x10\x05\x12\x16\n\x12JOB_UNINSTALLATION\x10\x06*\x7f\n\tValueType\x12\x0b\n\x07UNKNOWN\x10\x00\x12\x08\n\x04\x42OOL\x10\x01\x12\t\n\x05\x42YTES\x10\x02\x12\n\n\x06\x44OUBLE\x10\x03\x12\n\n\x06SINT64\x10\x04\x12\n\n\x06STRING\x10\x05\x12\x0b\n\x07GPSDATA\x10\x06\x12\x08\n\x04LIST\x10\x07\x12\x15\n\x11\x43LASSIFICATION_ND\x10\x08')

_MARKERTYPE = DESCRIPTOR.enum_types_by_name['MarkerType']
MarkerType = enum_type_wrapper.EnumTypeWrapper(_MARKERTYPE)
_VALUETYPE = DESCRIPTOR.enum_types_by_name['ValueType']
ValueType = enum_type_wrapper.EnumTypeWrapper(_VALUETYPE)
START_TRIGGER = 0
STOP_TRIGGER = 1
DRIVE_CYCLE_START = 2
DRIVE_CYCLE_END = 3
GENERIC_EVENT = 4
JOB_INSTALLATION = 5
JOB_UNINSTALLATION = 6
UNKNOWN = 0
BOOL = 1
BYTES = 2
DOUBLE = 3
SINT64 = 4
STRING = 5
GPSDATA = 6
LIST = 7
CLASSIFICATION_ND = 8


_MEASUREMENT = DESCRIPTOR.message_types_by_name['Measurement']
_MARKER = DESCRIPTOR.message_types_by_name['Marker']
_MARKERDATA = DESCRIPTOR.message_types_by_name['MarkerData']
_SERIESGROUP = DESCRIPTOR.message_types_by_name['SeriesGroup']
_SERIES = DESCRIPTOR.message_types_by_name['Series']
_TIMEPOINT = DESCRIPTOR.message_types_by_name['TimePoint']
_DATAPOINT = DESCRIPTOR.message_types_by_name['DataPoint']
_VALUE = DESCRIPTOR.message_types_by_name['Value']
_SCALARVALUE = DESCRIPTOR.message_types_by_name['ScalarValue']
_NUMBERVALUE = DESCRIPTOR.message_types_by_name['NumberValue']
_GPSDATA = DESCRIPTOR.message_types_by_name['GPSData']
_SCALARLIST = DESCRIPTOR.message_types_by_name['ScalarList']
_CLASSIFICATIONND = DESCRIPTOR.message_types_by_name['ClassificationND']
_CLASSIFICATIONLIST = DESCRIPTOR.message_types_by_name['ClassificationList']
_CLASSIFICATIONVALUE = DESCRIPTOR.message_types_by_name['ClassificationValue']
_AXIS = DESCRIPTOR.message_types_by_name['Axis']
Measurement = _reflection.GeneratedProtocolMessageType('Measurement', (_message.Message,), {
  'DESCRIPTOR' : _MEASUREMENT,
  '__module__' : 'Measurement_v3_pb2'
  # @@protoc_insertion_point(class_scope:RemoteMeasurement_v3.Measurement)
  })
_sym_db.RegisterMessage(Measurement)

Marker = _reflection.GeneratedProtocolMessageType('Marker', (_message.Message,), {
  'DESCRIPTOR' : _MARKER,
  '__module__' : 'Measurement_v3_pb2'
  # @@protoc_insertion_point(class_scope:RemoteMeasurement_v3.Marker)
  })
_sym_db.RegisterMessage(Marker)

MarkerData = _reflection.GeneratedProtocolMessageType('MarkerData', (_message.Message,), {
  'DESCRIPTOR' : _MARKERDATA,
  '__module__' : 'Measurement_v3_pb2'
  # @@protoc_insertion_point(class_scope:RemoteMeasurement_v3.MarkerData)
  })
_sym_db.RegisterMessage(MarkerData)

SeriesGroup = _reflection.GeneratedProtocolMessageType('SeriesGroup', (_message.Message,), {
  'DESCRIPTOR' : _SERIESGROUP,
  '__module__' : 'Measurement_v3_pb2'
  # @@protoc_insertion_point(class_scope:RemoteMeasurement_v3.SeriesGroup)
  })
_sym_db.RegisterMessage(SeriesGroup)

Series = _reflection.GeneratedProtocolMessageType('Series', (_message.Message,), {
  'DESCRIPTOR' : _SERIES,
  '__module__' : 'Measurement_v3_pb2'
  # @@protoc_insertion_point(class_scope:RemoteMeasurement_v3.Series)
  })
_sym_db.RegisterMessage(Series)

TimePoint = _reflection.GeneratedProtocolMessageType('TimePoint', (_message.Message,), {
  'DESCRIPTOR' : _TIMEPOINT,
  '__module__' : 'Measurement_v3_pb2'
  # @@protoc_insertion_point(class_scope:RemoteMeasurement_v3.TimePoint)
  })
_sym_db.RegisterMessage(TimePoint)

DataPoint = _reflection.GeneratedProtocolMessageType('DataPoint', (_message.Message,), {
  'DESCRIPTOR' : _DATAPOINT,
  '__module__' : 'Measurement_v3_pb2'
  # @@protoc_insertion_point(class_scope:RemoteMeasurement_v3.DataPoint)
  })
_sym_db.RegisterMessage(DataPoint)

Value = _reflection.GeneratedProtocolMessageType('Value', (_message.Message,), {
  'DESCRIPTOR' : _VALUE,
  '__module__' : 'Measurement_v3_pb2'
  # @@protoc_insertion_point(class_scope:RemoteMeasurement_v3.Value)
  })
_sym_db.RegisterMessage(Value)

ScalarValue = _reflection.GeneratedProtocolMessageType('ScalarValue', (_message.Message,), {
  'DESCRIPTOR' : _SCALARVALUE,
  '__module__' : 'Measurement_v3_pb2'
  # @@protoc_insertion_point(class_scope:RemoteMeasurement_v3.ScalarValue)
  })
_sym_db.RegisterMessage(ScalarValue)

NumberValue = _reflection.GeneratedProtocolMessageType('NumberValue', (_message.Message,), {
  'DESCRIPTOR' : _NUMBERVALUE,
  '__module__' : 'Measurement_v3_pb2'
  # @@protoc_insertion_point(class_scope:RemoteMeasurement_v3.NumberValue)
  })
_sym_db.RegisterMessage(NumberValue)

GPSData = _reflection.GeneratedProtocolMessageType('GPSData', (_message.Message,), {
  'DESCRIPTOR' : _GPSDATA,
  '__module__' : 'Measurement_v3_pb2'
  # @@protoc_insertion_point(class_scope:RemoteMeasurement_v3.GPSData)
  })
_sym_db.RegisterMessage(GPSData)

ScalarList = _reflection.GeneratedProtocolMessageType('ScalarList', (_message.Message,), {
  'DESCRIPTOR' : _SCALARLIST,
  '__module__' : 'Measurement_v3_pb2'
  # @@protoc_insertion_point(class_scope:RemoteMeasurement_v3.ScalarList)
  })
_sym_db.RegisterMessage(ScalarList)

ClassificationND = _reflection.GeneratedProtocolMessageType('ClassificationND', (_message.Message,), {
  'DESCRIPTOR' : _CLASSIFICATIONND,
  '__module__' : 'Measurement_v3_pb2'
  # @@protoc_insertion_point(class_scope:RemoteMeasurement_v3.ClassificationND)
  })
_sym_db.RegisterMessage(ClassificationND)

ClassificationList = _reflection.GeneratedProtocolMessageType('ClassificationList', (_message.Message,), {
  'DESCRIPTOR' : _CLASSIFICATIONLIST,
  '__module__' : 'Measurement_v3_pb2'
  # @@protoc_insertion_point(class_scope:RemoteMeasurement_v3.ClassificationList)
  })
_sym_db.RegisterMessage(ClassificationList)

ClassificationValue = _reflection.GeneratedProtocolMessageType('ClassificationValue', (_message.Message,), {
  'DESCRIPTOR' : _CLASSIFICATIONVALUE,
  '__module__' : 'Measurement_v3_pb2'
  # @@protoc_insertion_point(class_scope:RemoteMeasurement_v3.ClassificationValue)
  })
_sym_db.RegisterMessage(ClassificationValue)

Axis = _reflection.GeneratedProtocolMessageType('Axis', (_message.Message,), {
  'DESCRIPTOR' : _AXIS,
  '__module__' : 'Measurement_v3_pb2'
  # @@protoc_insertion_point(class_scope:RemoteMeasurement_v3.Axis)
  })
_sym_db.RegisterMessage(Axis)

if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  _MARKERTYPE._serialized_start=1975
  _MARKERTYPE._serialized_end=2133
  _VALUETYPE._serialized_start=2135
  _VALUETYPE._serialized_end=2262
  _MEASUREMENT._serialized_start=47
  _MEASUREMENT._serialized_end=190
  _MARKER._serialized_start=193
  _MARKER._serialized_end=331
  _MARKERDATA._serialized_start=333
  _MARKERDATA._serialized_end=374
  _SERIESGROUP._serialized_start=376
  _SERIESGROUP._serialized_end=488
  _SERIES._serialized_start=490
  _SERIES._serialized_end=591
  _TIMEPOINT._serialized_start=593
  _TIMEPOINT._serialized_end=676
  _DATAPOINT._serialized_start=678
  _DATAPOINT._serialized_end=753
  _VALUE._serialized_start=756
  _VALUE._serialized_end=1001
  _SCALARVALUE._serialized_start=1004
  _SCALARVALUE._serialized_end=1137
  _NUMBERVALUE._serialized_start=1139
  _NUMBERVALUE._serialized_end=1196
  _GPSDATA._serialized_start=1199
  _GPSDATA._serialized_end=1347
  _SCALARLIST._serialized_start=1349
  _SCALARLIST._serialized_end=1411
  _CLASSIFICATIONND._serialized_start=1414
  _CLASSIFICATIONND._serialized_end=1542
  _CLASSIFICATIONLIST._serialized_start=1544
  _CLASSIFICATIONLIST._serialized_end=1622
  _CLASSIFICATIONVALUE._serialized_start=1625
  _CLASSIFICATIONVALUE._serialized_end=1775
  _AXIS._serialized_start=1778
  _AXIS._serialized_end=1972
# @@protoc_insertion_point(module_scope)
