# -*- coding: UTF-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

__author__ = "d01"
__email__ = "jungflor@gmail.com"
__copyright__ = "Copyright (C) 2015-16, Florian JUNG"
__license__ = "MIT"
__version__ = "0.1.1"
__date__ = "2016-04-02"
# Created: 2015-06-27 17:33

import logging
from pprint import pformat
import threading
import time

from twisted.logger import STDLibLogObserver, globalLogBeginner
from twisted.internet import reactor
from autobahn.twisted.websocket import WebSocketServerFactory, \
    WebSocketServerProtocol
from twisted.internet.error import ReactorAlreadyRunning
from flotils.loadable import loadJSON, saveJSON

from paps_settings import SettablePlugin


logger = logging.getLogger(__name__)


class RealTimePluginProtocol(WebSocketServerProtocol):
    """ Websocket linking the plugin to the browser """

    def onConnect(self, request):
        logger.debug(u"Server connecting: {}".format(request.peer))

    def onOpen(self):
        logger.debug("WebSocket connection open.")
        self._rt._plugin_protocol = self

    def onMessage(self, payload, isBinary):
        if not isBinary:
            payload = loadJSON(payload.decode("utf8"))
            try:
                res = self._rt.handle_msg(payload)
            except:
                logger.exception(u"Failed to handle {}".format(payload))
                return
            if res:
                self.sendMessage(saveJSON(res, pretty=False).encode("utf8"))
        else:
            logger.warning("Unsupported: Received binary payload")

    def onClose(self, wasClean, code, reason):
        logger.debug(u"WebSocket connection closed: {}".format(reason))
        self._rt._plugin_protocol = None


class RealTime(SettablePlugin):
    """ Class doing realtime forwarding of person events """

    def __init__(self, settings=None):
        if settings is None:
            settings = {}
        super(RealTime, self).__init__(settings)
        self._host = settings.get('host', "localhost")
        """ Bind websocket server to address
            :type : unicode """
        self._port = settings.get('port', 5000)
        """ Bind websocket server to port
            :type : int """
        self._ws_path = settings.get('ws_path', "")
        """ Bind websocket to path
            :type : unicode """
        self._is_debug = settings.get('use_debug', False)
        """ Use debug mode
            :type : bool """
        self._factory = None
        """ Factory for the web socket
            :type : None | autobahn.twisted.websocket.WebSocketServerFactory """
        self._plugin_protocol = None
        """ Handle to plugin client protocol
            :type : None | RealTimePluginProtocol """
        self._reactor_shutdown = True
        """ Does the reactor need to be shutdown
            :type : bool """

    def get_info(self):
        info = super(RealTime, self).get_info()
        info['description'] = "Show changes in browser"
        return info

    def get_data(self):
        res = super(RealTime, self).get_data()
        res['websocket'] = u"ws://{}:{}{}".format(
            self._host, self._port, self._ws_path
        )
        return res

    def send_message(self, msg):
        """
        Send a message over the protocol to the client

        :param msg: Message to send to client
        :type msg: str | unicode
        :rtype: None
        """
        try:
            if self._plugin_protocol is None:
                self.warning("No protocol connected")
            else:
                self._plugin_protocol.sendMessage(msg)
        except:
            self.exception(u"Failed to send message: {}".format(msg))

    def on_person_new(self, people):
        msg = {
            'event': "person_new",
            'people': [p.to_dict() for p in people]
        }
        self.send_message(saveJSON(msg, pretty=False).encode("utf8"))

    def on_person_leave(self, people):
        msg = {
            'event': "person_leave",
            'people': [p.to_dict() for p in people]
        }
        self.send_message(saveJSON(msg, pretty=False).encode("utf8"))

    def on_person_update(self, people):
        msg = {
            'event': "person_update",
            'people': [p.to_dict() for p in people]
        }
        self.send_message(saveJSON(msg, pretty=False).encode("utf8"))

    def handle_msg(self, payload):
        """
        Handle message for network plugin protocol

        :param payload: Received message
        :type payload: dict
        :return: Response to send (if set)
        :rtype: None | dict
        """
        self.debug(u"\n{}".format(pformat(payload)))

    def _reactor_start(self):
        """
        Start the reactor if it is not already running
        If someone else started it -> someone else should shut it down
        """
        try:
            if reactor.running:
                observer = STDLibLogObserver(name='twisted')
                globalLogBeginner.beginLoggingTo([observer])
                reactor.run(False)
            else:
                self.info("Reactor already running")
                self._reactor_shutdown = False
        except ReactorAlreadyRunning:
            self.info("Reactor already running")
            self._reactor_shutdown = False
        except:
            self.exception("Failed to start reactor")

    def start(self, blocking=False):
        self.debug("()")
        if self._is_running:
            self.debug("Already running")
            return

        self._factory = WebSocketServerFactory(
            u"ws://{}:{}{}".format(self._host, self._port, self._ws_path)
        )

        self._factory.protocol = RealTimePluginProtocol
        self._factory.protocol._rt = self
        # self._factory.protocol.onOpen = self._on_ws_open

        reactor.listenTCP(self._port, self._factory)
        # False or dict alone should be enough
        a_thread = threading.Thread(
            target=self._reactor_start
        )
        a_thread.daemon = True
        a_thread.start()
        super(RealTime, self).start(blocking)

    def stop(self):
        self.debug("()")
        if not self._is_running:
            return
        if self._plugin_protocol:
            reactor.callFromThread(self._plugin_protocol.sendClose)
            time.sleep(1)
        if self._reactor_shutdown:
            reactor.callFromThread(reactor.stop)
        self._factory = None
