# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: gps_position_report_event.proto
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


import src.resources.proto_py.device_to_backend_message_meta_pb2 as device__to__backend__message__meta__pb2


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x1fgps_position_report_event.proto\x1a$device_to_backend_message_meta.proto\"\xda\x01\n\x16GpsPositionReportEvent\x12,\n\x04meta\x18\x85\xac\xcc\x01 \x01(\x0b\x32\x1b.DeviceToBackendMessageMeta\x12\x14\n\tlongitude\x18\xaf\x93\xc0\x41 \x01(\x02\x12\x14\n\x08latitude\x18\x96\xa7\xd1\xae\x01 \x01(\x02\x12\x14\n\x08\x61ltitude\x18\xa5\x95\x8d\xcb\x01 \x01(\x02\x12\x12\n\x07heading\x18\x83\xfc\x9d{ \x01(\x05\x12\x10\n\x05speed\x18\xc7\x80\xa4\x34 \x01(\x02\x12\x14\n\x08\x61\x63\x63uracy\x18\x8a\x8e\xbd\xf8\x01 \x01(\x02\x12\x14\n\ttimestamp\x18\x96\xd2\xa4\x1a \x01(\x03P\x00\x62\x06proto3')



_GPSPOSITIONREPORTEVENT = DESCRIPTOR.message_types_by_name['GpsPositionReportEvent']
GpsPositionReportEvent = _reflection.GeneratedProtocolMessageType('GpsPositionReportEvent', (_message.Message,), {
  'DESCRIPTOR' : _GPSPOSITIONREPORTEVENT,
  '__module__' : 'gps_position_report_event_pb2'
  # @@protoc_insertion_point(class_scope:GpsPositionReportEvent)
  })
_sym_db.RegisterMessage(GpsPositionReportEvent)

if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  _GPSPOSITIONREPORTEVENT._serialized_start=74
  _GPSPOSITIONREPORTEVENT._serialized_end=292
# @@protoc_insertion_point(module_scope)