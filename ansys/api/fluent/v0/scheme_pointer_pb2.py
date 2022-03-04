# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: scheme_pointer.proto

from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


import ansys.api.fluent.v0.common_pb2 as common__pb2


DESCRIPTOR = _descriptor.FileDescriptor(
  name='scheme_pointer.proto',
  package='grpcRemoting',
  syntax='proto3',
  serialized_options=None,
  create_key=_descriptor._internal_create_key,
  serialized_pb=b'\n\x14scheme_pointer.proto\x12\x0cgrpcRemoting\x1a\x0c\x63ommon.proto\"\xb4\x02\n\rSchemePointer\x12$\n\x05\x65mpty\x18\x01 \x01(\x0b\x32\x13.grpcRemoting.EmptyH\x00\x12\r\n\x03sym\x18\x02 \x01(\tH\x00\x12\x36\n\x04pair\x18\x03 \x01(\x0b\x32&.grpcRemoting.SchemePointer.SchemePairH\x00\x12\x10\n\x06\x66lonum\x18\x04 \x01(\x01H\x00\x12\x12\n\x08\x66ixednum\x18\x05 \x01(\x12H\x00\x12\x0b\n\x01\x63\x18\x06 \x01(\tH\x00\x12\r\n\x03str\x18\x07 \x01(\tH\x00\x12\x0b\n\x01\x62\x18\x08 \x01(\x08H\x00\x1a`\n\nSchemePair\x12(\n\x03\x63\x61r\x18\x01 \x01(\x0b\x32\x1b.grpcRemoting.SchemePointer\x12(\n\x03\x63\x64r\x18\x02 \x01(\x0b\x32\x1b.grpcRemoting.SchemePointerB\x05\n\x03valb\x06proto3'
  ,
  dependencies=[common__pb2.DESCRIPTOR,])




_SCHEMEPOINTER_SCHEMEPAIR = _descriptor.Descriptor(
  name='SchemePair',
  full_name='grpcRemoting.SchemePointer.SchemePair',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='car', full_name='grpcRemoting.SchemePointer.SchemePair.car', index=0,
      number=1, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='cdr', full_name='grpcRemoting.SchemePointer.SchemePair.cdr', index=1,
      number=2, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=258,
  serialized_end=354,
)

_SCHEMEPOINTER = _descriptor.Descriptor(
  name='SchemePointer',
  full_name='grpcRemoting.SchemePointer',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='empty', full_name='grpcRemoting.SchemePointer.empty', index=0,
      number=1, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='sym', full_name='grpcRemoting.SchemePointer.sym', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='pair', full_name='grpcRemoting.SchemePointer.pair', index=2,
      number=3, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='flonum', full_name='grpcRemoting.SchemePointer.flonum', index=3,
      number=4, type=1, cpp_type=5, label=1,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='fixednum', full_name='grpcRemoting.SchemePointer.fixednum', index=4,
      number=5, type=18, cpp_type=2, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='c', full_name='grpcRemoting.SchemePointer.c', index=5,
      number=6, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='str', full_name='grpcRemoting.SchemePointer.str', index=6,
      number=7, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='b', full_name='grpcRemoting.SchemePointer.b', index=7,
      number=8, type=8, cpp_type=7, label=1,
      has_default_value=False, default_value=False,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[_SCHEMEPOINTER_SCHEMEPAIR, ],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
    _descriptor.OneofDescriptor(
      name='val', full_name='grpcRemoting.SchemePointer.val',
      index=0, containing_type=None,
      create_key=_descriptor._internal_create_key,
    fields=[]),
  ],
  serialized_start=53,
  serialized_end=361,
)

_SCHEMEPOINTER_SCHEMEPAIR.fields_by_name['car'].message_type = _SCHEMEPOINTER
_SCHEMEPOINTER_SCHEMEPAIR.fields_by_name['cdr'].message_type = _SCHEMEPOINTER
_SCHEMEPOINTER_SCHEMEPAIR.containing_type = _SCHEMEPOINTER
_SCHEMEPOINTER.fields_by_name['empty'].message_type = common__pb2._EMPTY
_SCHEMEPOINTER.fields_by_name['pair'].message_type = _SCHEMEPOINTER_SCHEMEPAIR
_SCHEMEPOINTER.oneofs_by_name['val'].fields.append(
  _SCHEMEPOINTER.fields_by_name['empty'])
_SCHEMEPOINTER.fields_by_name['empty'].containing_oneof = _SCHEMEPOINTER.oneofs_by_name['val']
_SCHEMEPOINTER.oneofs_by_name['val'].fields.append(
  _SCHEMEPOINTER.fields_by_name['sym'])
_SCHEMEPOINTER.fields_by_name['sym'].containing_oneof = _SCHEMEPOINTER.oneofs_by_name['val']
_SCHEMEPOINTER.oneofs_by_name['val'].fields.append(
  _SCHEMEPOINTER.fields_by_name['pair'])
_SCHEMEPOINTER.fields_by_name['pair'].containing_oneof = _SCHEMEPOINTER.oneofs_by_name['val']
_SCHEMEPOINTER.oneofs_by_name['val'].fields.append(
  _SCHEMEPOINTER.fields_by_name['flonum'])
_SCHEMEPOINTER.fields_by_name['flonum'].containing_oneof = _SCHEMEPOINTER.oneofs_by_name['val']
_SCHEMEPOINTER.oneofs_by_name['val'].fields.append(
  _SCHEMEPOINTER.fields_by_name['fixednum'])
_SCHEMEPOINTER.fields_by_name['fixednum'].containing_oneof = _SCHEMEPOINTER.oneofs_by_name['val']
_SCHEMEPOINTER.oneofs_by_name['val'].fields.append(
  _SCHEMEPOINTER.fields_by_name['c'])
_SCHEMEPOINTER.fields_by_name['c'].containing_oneof = _SCHEMEPOINTER.oneofs_by_name['val']
_SCHEMEPOINTER.oneofs_by_name['val'].fields.append(
  _SCHEMEPOINTER.fields_by_name['str'])
_SCHEMEPOINTER.fields_by_name['str'].containing_oneof = _SCHEMEPOINTER.oneofs_by_name['val']
_SCHEMEPOINTER.oneofs_by_name['val'].fields.append(
  _SCHEMEPOINTER.fields_by_name['b'])
_SCHEMEPOINTER.fields_by_name['b'].containing_oneof = _SCHEMEPOINTER.oneofs_by_name['val']
DESCRIPTOR.message_types_by_name['SchemePointer'] = _SCHEMEPOINTER
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

SchemePointer = _reflection.GeneratedProtocolMessageType('SchemePointer', (_message.Message,), {

  'SchemePair' : _reflection.GeneratedProtocolMessageType('SchemePair', (_message.Message,), {
    'DESCRIPTOR' : _SCHEMEPOINTER_SCHEMEPAIR,
    '__module__' : 'scheme_pointer_pb2'
    # @@protoc_insertion_point(class_scope:grpcRemoting.SchemePointer.SchemePair)
    })
  ,
  'DESCRIPTOR' : _SCHEMEPOINTER,
  '__module__' : 'scheme_pointer_pb2'
  # @@protoc_insertion_point(class_scope:grpcRemoting.SchemePointer)
  })
_sym_db.RegisterMessage(SchemePointer)
_sym_db.RegisterMessage(SchemePointer.SchemePair)


# @@protoc_insertion_point(module_scope)
