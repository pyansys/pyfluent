# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc

import ansys.api.fluent.v0.datamodel_se_pb2 as datamodel__se__pb2


class DataModelStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.BeginStreaming = channel.unary_stream(
                '/grpcRemoting.DataModel/BeginStreaming',
                request_serializer=datamodel__se__pb2.DataModelRequest.SerializeToString,
                response_deserializer=datamodel__se__pb2.DataModelResponse.FromString,
                )
        self.initDatamodel = channel.unary_unary(
                '/grpcRemoting.DataModel/initDatamodel',
                request_serializer=datamodel__se__pb2.InitDatamodelRequest.SerializeToString,
                response_deserializer=datamodel__se__pb2.InitDatamodelResponse.FromString,
                )
        self.getState = channel.unary_unary(
                '/grpcRemoting.DataModel/getState',
                request_serializer=datamodel__se__pb2.GetStateRequest.SerializeToString,
                response_deserializer=datamodel__se__pb2.GetStateResponse.FromString,
                )
        self.setState = channel.unary_unary(
                '/grpcRemoting.DataModel/setState',
                request_serializer=datamodel__se__pb2.SetStateRequest.SerializeToString,
                response_deserializer=datamodel__se__pb2.SetStateResponse.FromString,
                )
        self.updateDict = channel.unary_unary(
                '/grpcRemoting.DataModel/updateDict',
                request_serializer=datamodel__se__pb2.UpdateDictRequest.SerializeToString,
                response_deserializer=datamodel__se__pb2.UpdateDictResponse.FromString,
                )
        self.deleteObject = channel.unary_unary(
                '/grpcRemoting.DataModel/deleteObject',
                request_serializer=datamodel__se__pb2.DeleteObjectRequest.SerializeToString,
                response_deserializer=datamodel__se__pb2.DeleteObjectResponse.FromString,
                )
        self.getAttributeValue = channel.unary_unary(
                '/grpcRemoting.DataModel/getAttributeValue',
                request_serializer=datamodel__se__pb2.GetAttributeValueRequest.SerializeToString,
                response_deserializer=datamodel__se__pb2.GetAttributeValueResponse.FromString,
                )
        self.executeCommand = channel.unary_unary(
                '/grpcRemoting.DataModel/executeCommand',
                request_serializer=datamodel__se__pb2.ExecuteCommandRequest.SerializeToString,
                response_deserializer=datamodel__se__pb2.ExecuteCommandResponse.FromString,
                )
        self.getSpecs = channel.unary_unary(
                '/grpcRemoting.DataModel/getSpecs',
                request_serializer=datamodel__se__pb2.GetSpecsRequest.SerializeToString,
                response_deserializer=datamodel__se__pb2.GetSpecsResponse.FromString,
                )


class DataModelServicer(object):
    """Missing associated documentation comment in .proto file."""

    def BeginStreaming(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def initDatamodel(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def getState(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def setState(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def updateDict(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def deleteObject(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def getAttributeValue(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def executeCommand(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def getSpecs(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_DataModelServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'BeginStreaming': grpc.unary_stream_rpc_method_handler(
                    servicer.BeginStreaming,
                    request_deserializer=datamodel__se__pb2.DataModelRequest.FromString,
                    response_serializer=datamodel__se__pb2.DataModelResponse.SerializeToString,
            ),
            'initDatamodel': grpc.unary_unary_rpc_method_handler(
                    servicer.initDatamodel,
                    request_deserializer=datamodel__se__pb2.InitDatamodelRequest.FromString,
                    response_serializer=datamodel__se__pb2.InitDatamodelResponse.SerializeToString,
            ),
            'getState': grpc.unary_unary_rpc_method_handler(
                    servicer.getState,
                    request_deserializer=datamodel__se__pb2.GetStateRequest.FromString,
                    response_serializer=datamodel__se__pb2.GetStateResponse.SerializeToString,
            ),
            'setState': grpc.unary_unary_rpc_method_handler(
                    servicer.setState,
                    request_deserializer=datamodel__se__pb2.SetStateRequest.FromString,
                    response_serializer=datamodel__se__pb2.SetStateResponse.SerializeToString,
            ),
            'updateDict': grpc.unary_unary_rpc_method_handler(
                    servicer.updateDict,
                    request_deserializer=datamodel__se__pb2.UpdateDictRequest.FromString,
                    response_serializer=datamodel__se__pb2.UpdateDictResponse.SerializeToString,
            ),
            'deleteObject': grpc.unary_unary_rpc_method_handler(
                    servicer.deleteObject,
                    request_deserializer=datamodel__se__pb2.DeleteObjectRequest.FromString,
                    response_serializer=datamodel__se__pb2.DeleteObjectResponse.SerializeToString,
            ),
            'getAttributeValue': grpc.unary_unary_rpc_method_handler(
                    servicer.getAttributeValue,
                    request_deserializer=datamodel__se__pb2.GetAttributeValueRequest.FromString,
                    response_serializer=datamodel__se__pb2.GetAttributeValueResponse.SerializeToString,
            ),
            'executeCommand': grpc.unary_unary_rpc_method_handler(
                    servicer.executeCommand,
                    request_deserializer=datamodel__se__pb2.ExecuteCommandRequest.FromString,
                    response_serializer=datamodel__se__pb2.ExecuteCommandResponse.SerializeToString,
            ),
            'getSpecs': grpc.unary_unary_rpc_method_handler(
                    servicer.getSpecs,
                    request_deserializer=datamodel__se__pb2.GetSpecsRequest.FromString,
                    response_serializer=datamodel__se__pb2.GetSpecsResponse.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'grpcRemoting.DataModel', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class DataModel(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def BeginStreaming(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_stream(request, target, '/grpcRemoting.DataModel/BeginStreaming',
            datamodel__se__pb2.DataModelRequest.SerializeToString,
            datamodel__se__pb2.DataModelResponse.FromString,
            options, channel_credentials,
            call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def initDatamodel(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/grpcRemoting.DataModel/initDatamodel',
            datamodel__se__pb2.InitDatamodelRequest.SerializeToString,
            datamodel__se__pb2.InitDatamodelResponse.FromString,
            options, channel_credentials,
            call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def getState(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/grpcRemoting.DataModel/getState',
            datamodel__se__pb2.GetStateRequest.SerializeToString,
            datamodel__se__pb2.GetStateResponse.FromString,
            options, channel_credentials,
            call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def setState(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/grpcRemoting.DataModel/setState',
            datamodel__se__pb2.SetStateRequest.SerializeToString,
            datamodel__se__pb2.SetStateResponse.FromString,
            options, channel_credentials,
            call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def updateDict(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/grpcRemoting.DataModel/updateDict',
            datamodel__se__pb2.UpdateDictRequest.SerializeToString,
            datamodel__se__pb2.UpdateDictResponse.FromString,
            options, channel_credentials,
            call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def deleteObject(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/grpcRemoting.DataModel/deleteObject',
            datamodel__se__pb2.DeleteObjectRequest.SerializeToString,
            datamodel__se__pb2.DeleteObjectResponse.FromString,
            options, channel_credentials,
            call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def getAttributeValue(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/grpcRemoting.DataModel/getAttributeValue',
            datamodel__se__pb2.GetAttributeValueRequest.SerializeToString,
            datamodel__se__pb2.GetAttributeValueResponse.FromString,
            options, channel_credentials,
            call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def executeCommand(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/grpcRemoting.DataModel/executeCommand',
            datamodel__se__pb2.ExecuteCommandRequest.SerializeToString,
            datamodel__se__pb2.ExecuteCommandResponse.FromString,
            options, channel_credentials,
            call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def getSpecs(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/grpcRemoting.DataModel/getSpecs',
            datamodel__se__pb2.GetSpecsRequest.SerializeToString,
            datamodel__se__pb2.GetSpecsResponse.FromString,
            options, channel_credentials,
            call_credentials, compression, wait_for_ready, timeout, metadata)
