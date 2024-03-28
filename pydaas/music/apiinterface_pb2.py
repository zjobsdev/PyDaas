# -*- coding: utf-8 -*-
# Copy from https://github.com/perillaroc/nuwe-cmadaas-python/blob/master/nuwe_cmadaas/music/apiinterface_pb2.py
# License perillaroc
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: apiinterface.proto
"""Generated protocol buffer code."""
from google.protobuf.internal import builder as _builder
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database

# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()

DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(
    b'\n\x12\x61piinterface.proto\x12\x0c\x63ma.music.pb\"\xc4\x01\n\x0bRequestInfo\x12\x11\n\terrorCode\x18\x01 \x01(\x05\x12\x14\n\x0c\x65rrorMessage\x18\x02 \x01(\t\x12\x14\n\x0crequestElems\x18\x03 \x01(\t\x12\x15\n\rrequestParams\x18\x04 \x01(\t\x12\x13\n\x0brequestTime\x18\x05 \x01(\t\x12\x14\n\x0cresponseTime\x18\x06 \x01(\t\x12\x10\n\x08rowCount\x18\x07 \x01(\x05\x12\x10\n\x08takeTime\x18\x08 \x01(\x05\x12\x10\n\x08\x63olCount\x18\t \x01(\x05\"\\\n\nRetArray2D\x12\x0c\n\x04\x64\x61ta\x18\x01 \x03(\t\x12*\n\x07request\x18\x02 \x01(\x0b\x32\x19.cma.music.pb.RequestInfo\x12\x14\n\x0c\x65lementNames\x18\x03 \x03(\t\"\x94\x02\n\x0eRetGridArray2D\x12\x0c\n\x04\x64\x61ta\x18\x01 \x03(\x02\x12*\n\x07request\x18\x02 \x01(\x0b\x32\x19.cma.music.pb.RequestInfo\x12\x10\n\x08startLat\x18\x03 \x01(\x02\x12\x10\n\x08startLon\x18\x04 \x01(\x02\x12\x0e\n\x06\x65ndLat\x18\x05 \x01(\x02\x12\x0e\n\x06\x65ndLon\x18\x06 \x01(\x02\x12\x10\n\x08latCount\x18\x07 \x01(\x05\x12\x10\n\x08lonCount\x18\x08 \x01(\x05\x12\x0f\n\x07lonStep\x18\t \x01(\x02\x12\x0f\n\x07latStep\x18\n \x01(\x02\x12\x0c\n\x04lats\x18\x0b \x03(\x02\x12\x0c\n\x04lons\x18\x0c \x03(\x02\x12\r\n\x05units\x18\r \x01(\t\x12\x13\n\x0buserEleName\x18\x0e \x01(\t\"\x84\x01\n\x08\x46ileInfo\x12\x10\n\x08\x66ileName\x18\x01 \x01(\t\x12\x10\n\x08savePath\x18\x02 \x01(\t\x12\x0e\n\x06suffix\x18\x03 \x01(\t\x12\x0c\n\x04size\x18\x04 \x01(\t\x12\x0f\n\x07\x66ileUrl\x18\x05 \x01(\t\x12\x11\n\timgBase64\x18\x06 \x01(\t\x12\x12\n\nattributes\x18\x07 \x03(\t\"e\n\x0cRetFilesInfo\x12)\n\tfileInfos\x18\x01 \x03(\x0b\x32\x16.cma.music.pb.FileInfo\x12*\n\x07request\x18\x02 \x01(\x0b\x32\x19.cma.music.pb.RequestInfo\"\xa7\x01\n\x0cStoreArray2D\x12\x0c\n\x04\x64\x61ta\x18\x01 \x03(\t\x12\x0b\n\x03row\x18\x02 \x01(\x05\x12\x0b\n\x03\x63ol\x18\x03 \x01(\x05\x12\x10\n\x08\x66ileflag\x18\x04 \x01(\x05\x12\x11\n\tfilenames\x18\x05 \x03(\t\x12\x14\n\x0cis_backstage\x18\x06 \x01(\x05\x12\x19\n\x11\x63lient_mount_path\x18\x07 \x01(\t\x12\x19\n\x11server_mount_path\x18\x08 \x01(\t\"_\n\x0cRetDataBlock\x12\x10\n\x08\x64\x61taName\x18\x01 \x01(\t\x12\x11\n\tbyteArray\x18\x02 \x01(\x0c\x12*\n\x07request\x18\x03 \x01(\x0b\x32\x19.cma.music.pb.RequestInfo\"\xab\x02\n\x0fRetGridVector2D\x12\x0f\n\x07u_datas\x18\x01 \x03(\x02\x12\x0f\n\x07v_data2\x18\x02 \x03(\x02\x12*\n\x07request\x18\x03 \x01(\x0b\x32\x19.cma.music.pb.RequestInfo\x12\x10\n\x08startLat\x18\x04 \x01(\x02\x12\x10\n\x08startLon\x18\x05 \x01(\x02\x12\x0e\n\x06\x65ndLat\x18\x06 \x01(\x02\x12\x0e\n\x06\x65ndLon\x18\x07 \x01(\x02\x12\x10\n\x08latCount\x18\x08 \x01(\x05\x12\x10\n\x08lonCount\x18\t \x01(\x05\x12\x0f\n\x07lonStep\x18\n \x01(\x02\x12\x0f\n\x07latStep\x18\x0b \x01(\x02\x12\x0c\n\x04lats\x18\x0c \x03(\x02\x12\x0c\n\x04lons\x18\r \x03(\x02\x12\x11\n\tu_EleName\x18\x0e \x01(\t\x12\x11\n\tv_EleName\x18\x0f \x01(\t\"\x96\x02\n\x0fRetGridScalar2D\x12\r\n\x05\x64\x61tas\x18\x01 \x03(\x02\x12*\n\x07request\x18\x02 \x01(\x0b\x32\x19.cma.music.pb.RequestInfo\x12\x10\n\x08startLat\x18\x03 \x01(\x02\x12\x10\n\x08startLon\x18\x04 \x01(\x02\x12\x0e\n\x06\x65ndLat\x18\x05 \x01(\x02\x12\x0e\n\x06\x65ndLon\x18\x06 \x01(\x02\x12\x10\n\x08latCount\x18\x07 \x01(\x05\x12\x10\n\x08lonCount\x18\x08 \x01(\x05\x12\x0f\n\x07lonStep\x18\t \x01(\x02\x12\x0f\n\x07latStep\x18\n \x01(\x02\x12\x0c\n\x04lats\x18\x0b \x03(\x02\x12\x0c\n\x04lons\x18\x0c \x03(\x02\x12\r\n\x05units\x18\r \x01(\t\x12\x13\n\x0buserEleName\x18\x0e \x01(\t\"a\n\rStoreGridData\x12\x12\n\nattributes\x18\x01 \x03(\t\x12\x11\n\tpointflag\x18\x02 \x01(\x05\x12\x0c\n\x04Lats\x18\x03 \x03(\x02\x12\x0c\n\x04Lons\x18\x04 \x03(\x02\x12\r\n\x05\x64\x61tas\x18\x05 \x03(\x02\"2\n\x0eStoreBlockData\x12\x12\n\nattributes\x18\x01 \x03(\t\x12\x0c\n\x04\x64\x61ta\x18\x02 \x01(\x0c\x62\x06proto3')

_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'apiinterface_pb2', globals())

if _descriptor._USE_C_DESCRIPTORS == False:
    DESCRIPTOR._options = None
    _REQUESTINFO._serialized_start = 37
    _REQUESTINFO._serialized_end = 233
    _RETARRAY2D._serialized_start = 235
    _RETARRAY2D._serialized_end = 327
    _RETGRIDARRAY2D._serialized_start = 330
    _RETGRIDARRAY2D._serialized_end = 606
    _FILEINFO._serialized_start = 609
    _FILEINFO._serialized_end = 741
    _RETFILESINFO._serialized_start = 743
    _RETFILESINFO._serialized_end = 844
    _STOREARRAY2D._serialized_start = 847
    _STOREARRAY2D._serialized_end = 1014
    _RETDATABLOCK._serialized_start = 1016
    _RETDATABLOCK._serialized_end = 1111
    _RETGRIDVECTOR2D._serialized_start = 1114
    _RETGRIDVECTOR2D._serialized_end = 1413
    _RETGRIDSCALAR2D._serialized_start = 1416
    _RETGRIDSCALAR2D._serialized_end = 1694
    _STOREGRIDDATA._serialized_start = 1696
    _STOREGRIDDATA._serialized_end = 1793
    _STOREBLOCKDATA._serialized_start = 1795
    _STOREBLOCKDATA._serialized_end = 1845
# @@protoc_insertion_point(module_scope)
