# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc

import ansys.api.fluent.v0.events_pb2 as events__pb2


class EventsStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.BeginStreaming = channel.unary_stream(
                '/grpcRemoting.Events/BeginStreaming',
                request_serializer=events__pb2.BeginStreamingRequest.SerializeToString,
                response_deserializer=events__pb2.BeginStreamingResponse.FromString,
                )


class EventsServicer(object):
    """Missing associated documentation comment in .proto file."""

    def BeginStreaming(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_EventsServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'BeginStreaming': grpc.unary_stream_rpc_method_handler(
                    servicer.BeginStreaming,
                    request_deserializer=events__pb2.BeginStreamingRequest.FromString,
                    response_serializer=events__pb2.BeginStreamingResponse.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'grpcRemoting.Events', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class Events(object):
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
        return grpc.experimental.unary_stream(request, target, '/grpcRemoting.Events/BeginStreaming',
            events__pb2.BeginStreamingRequest.SerializeToString,
            events__pb2.BeginStreamingResponse.FromString,
            options, channel_credentials,
            call_credentials, compression, wait_for_ready, timeout, metadata)
