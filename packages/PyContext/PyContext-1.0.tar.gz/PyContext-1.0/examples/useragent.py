from __future__ import with_statement
from context import layers
import httplib

class HTTPUserAgent(layers.Layer):
    def __init__(self, agent):
        self.agent = agent

class HTTPConnection(HTTPUserAgent, httplib.HTTPConnection):

    # Always add a User-Agent header
    @layers.before
    def endheaders(self, context):
        with layers.Disabled(HTTPUserAgent):
            self.putheader("User-Agent", context.layer.agent)

    # suppress other User-Agent headers added
    @layers.instead
    def putheader(self, context, header, value):
        if header.lower() == 'user-agent':
            return
        return context.proceed(header, value)
