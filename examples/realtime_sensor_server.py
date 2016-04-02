# -*- coding: UTF-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

__author__ = "d01"
__email__ = "jungflor@gmail.com"
__copyright__ = "Copyright (C) 2016, Florian JUNG"
__license__ = "MIT"
__version__ = "0.1.1"
__date__ = "2016-04-02"
# Created: 2016-03-03 19:50

from flotils.runable import SignalStopWrapper

from paps.si.app.sensorServer import SensorServer


class Testserver(SensorServer, SignalStopWrapper):
    pass


def do_test(c):
    import time
    time.sleep(10.0)
    c.on_person_new(people)
    time.sleep(2.0)
    c.on_person_update([Person("2.0", True)])
    time.sleep(2.0)
    c.on_person_update([Person("3.0", True)])
    time.sleep(2.0)
    c.on_person_update([Person("3.1", True), Person("3.0", True)])
    time.sleep(2.0)
    c.on_person_update([Person("2.0", False)])
    time.sleep(2.0)
    c.on_person_update([Person("2.1", True)])
    time.sleep(2.0)
    c.on_person_leave(people[:2])
    time.sleep(2.0)
    c.on_person_leave(people[2:])


if __name__ == "__main__":
    import logging
    import logging.config
    from flotils.logable import default_logging_config
    logging.config.dictConfig(default_logging_config)
    logging.getLogger().setLevel(logging.DEBUG)
    logging.getLogger("twisted").setLevel(logging.INFO)

    from paps_settings import SettingsPlugin
    from paps.crowd import CrowdController
    from paps_realtime import RealTime
    from paps import Person

    settings_client = SettingsPlugin({
        'host': "127.0.0.1",
        'port': 5000,
        'ws_path': "/ws",
        'use_debug': True,
        'controller': True
    })
    rt = RealTime({
        'host': "127.0.0.1",
        'port': 6789,
        'ws_path': "/real",
        'resource_path': "paps_realtime/resources/"
    })

    c = CrowdController({
        'plugins': [rt, settings_client]
    })

    t = Testserver({
        'multicast_bind_ip': "0.0.0.0",
        'listen_bind_ip': "0.0.0.0",
        'changer': c
    })
    people = [
        Person("2.0"),
        Person("2.1", True),
        Person("3.0", False),
        Person("3.1"),
    ]

    try:
        c.start(blocking=False)
        # t.start(blocking=True)
        t.start(False)
        do_test(c)
    finally:
        t.stop()
        c.stop()
