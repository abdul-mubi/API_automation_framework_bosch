# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: measurement_result_event.proto
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


import src.resources.proto_py.backend_to_device_message_meta_pb2 as backend__to__device__message__meta__pb2

DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x1emeasurement_result_event.proto\x12%com.bosch.bfb.protobuf.vehicledata.v3\x1a$device_to_backend_message_meta.proto\"\xb6\x02\n\x16MeasurementResultEvent\x12,\n\x04meta\x18\x85\xac\xcc\x01 \x01(\x0b\x32\x1b.DeviceToBackendMessageMeta\x12\x16\n\x0b\x61rtifactUri\x18\xc8\xc3\xed\x1a \x01(\t\x12\x19\n\rserialization\x18\xf1\xd7\x83\xb8\x01 \x01(\t\x12\x1c\n\x11measurementResult\x18\x89\xda\xdcP \x01(\t\x12\x14\n\tstackType\x18\xe5\x83\xf9\x37 \x01(\t\x12\x1a\n\x0e\x65xecutionStart\x18\xd8\x8f\xb8\xc2\x01 \x01(\t\x12\x17\n\x0c\x65xecutionEnd\x18\xdf\xe2\xb3\x44 \x01(\t\x12\x18\n\rmeasurementId\x18\xfa\xcb\xab\x15 \x01(\t\x12\x16\n\njobVersion\x18\xa7\xcb\xa8\x9c\x01 \x01(\t\x12\r\n\x03vin\x18\x9b\x90\x07 \x01(\t\x12\x11\n\x06isLast\x18\xa2\xa2\xea\x32 \x01(\tP\x00\x62\x06proto3')



_MEASUREMENTRESULTEVENT = DESCRIPTOR.message_types_by_name['MeasurementResultEvent']
MeasurementResultEvent = _reflection.GeneratedProtocolMessageType('MeasurementResultEvent', (_message.Message,), {
  'DESCRIPTOR' : _MEASUREMENTRESULTEVENT,
  '__module__' : 'measurement_result_event_pb2'
  # @@protoc_insertion_point(class_scope:com.bosch.bfb.protobuf.vehicledata.v3.MeasurementResultEvent)
  })
_sym_db.RegisterMessage(MeasurementResultEvent)

if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  _MEASUREMENTRESULTEVENT._serialized_start=112
  _MEASUREMENTRESULTEVENT._serialized_end=422
# @@protoc_insertion_point(module_scope)