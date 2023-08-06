# testutils.py
# -*- coding: utf8 -*-
# vim:fileencoding=utf8 ai ts=4 sts=4 et sw=4
# Copyright 2009 SKA South Africa (http://ska.ac.za/)
# BSD license - see COPYING for details

"""Test utils for katcp package tests.
   """

import client
import logging
import re
import time
import Queue
from .katcp import Sensor, Message, DeviceMetaclass
from .server import DeviceServer, FailReply

class TestLogHandler(logging.Handler):
    """A logger for KATCP tests."""

    def __init__(self):
        """Create a TestLogHandler."""
        logging.Handler.__init__(self)
        self._records = []

    def emit(self, record):
        """Handle the arrival of a log message."""
        self._records.append(record)

    def clear(self):
        """Clear the list of remembered logs."""
        self._records = []


class DeviceTestSensor(Sensor):
    """Test sensor."""

    def __init__(self, sensor_type, name, description, units, params,
                 timestamp, status, value):
        super(DeviceTestSensor, self).__init__(
            sensor_type, name, description, units, params)
        self.set(timestamp, status, value)


class TestClientMetaclass(DeviceMetaclass):
    """Metaclass for test client classes.

       Adds a raw send method and methods for collecting all inform and
       reply messages received by the client.
       """
    def __init__(mcs, name, bases, dct):
        """Constructor for TestClientMetaclass.  Should not be used
           directly.

           @param mcs The metaclass instance
           @param name The metaclass name
           @param bases List of base classes
           @param dct Class dict
        """
        super(TestClientMetaclass, mcs).__init__(name, bases, dct)

        orig_init = mcs.__init__
        orig_handle_reply = mcs.handle_reply
        orig_handle_inform = mcs.handle_inform

        def __init__(self, *args, **kwargs):
            orig_init(self, *args, **kwargs)
            self.clear_messages()

        def handle_reply(self, msg):
            self._replies.append(msg)
            self._msgs.append(msg)
            return orig_handle_reply(self, msg)

        def handle_inform(self, msg):
            self._informs.append(msg)
            self._msgs.append(msg)
            return orig_handle_inform(self, msg)

        def raw_send(self, chunk):
            """Send a raw chunk of data to the server."""
            self._sock.send(chunk)

        def replies_and_informs(self):
            return self._replies, self._informs

        def messages(self):
            return self._msgs

        def clear_messages(self):
            self._replies = []
            self._informs = []
            self._msgs = []

        mcs.__init__ = __init__
        mcs.handle_reply = handle_reply
        mcs.handle_inform = handle_inform
        mcs.raw_send = raw_send
        mcs.replies_and_informs = replies_and_informs
        mcs.messages = messages
        mcs.clear_messages = clear_messages


class DeviceTestClient(client.DeviceClient):
    """Test client."""
    __metaclass__ = TestClientMetaclass


class CallbackTestClient(client.CallbackClient):
    """Test callback client."""
    __metaclass__ = TestClientMetaclass


class BlockingTestClient(client.BlockingClient):
    """Test blocking client."""
    __metaclass__ = TestClientMetaclass

    def get_sensor_value(self, sensorname):
        reply, informs = self.blocking_request(Message.request("sensor-value", sensorname))

        if str(reply) == "!sensor-value ok 1":
            value = str(informs[0]).split(" ")[5]
        else:
            raise ValueError(str(reply))
        return value


class DeviceTestServer(DeviceServer):
    """Test server."""

    def __init__(self, *args, **kwargs):
        super(DeviceTestServer, self).__init__(*args, **kwargs)
        self.__msgs = []
        self.restart_queue = Queue.Queue()
        self.set_restart_queue(self.restart_queue)

    def setup_sensors(self):
        self.restarted = False
        self.add_sensor(DeviceTestSensor(
            Sensor.INTEGER, "an.int", "An Integer.", "count",
            [-5, 5],
            timestamp=12345, status=Sensor.NOMINAL, value=3
        ))

    def request_new_command(self, sock, msg):
        """A new command."""
        return Message.reply(msg.name, "ok", "param1", "param2")

    def request_raise_exception(self, sock, msg):
        """A handler which raises an exception."""
        raise Exception("An exception occurred!")

    def request_raise_fail(self, sock, msg):
        """A handler which raises a FailReply."""
        raise FailReply("There was a problem with your request.")

    def request_slow_command(self, sock, msg):
        """A slow command, sleeps for msg.arguments[0]"""
        time.sleep(float(msg.arguments[0]))
        return Message.reply(msg.name, "ok", msgid=msg.mid)

    def handle_message(self, sock, msg):
        self.__msgs.append(msg)
        super(DeviceTestServer, self).handle_message(sock, msg)

    def messages(self):
        return self.__msgs


class TestUtilMixin(object):
    """Mixin class implementing test helper methods for making
       assertions about lists of KATCP messages.
       """

    def _assert_msgs_length(self, actual_msgs, expected_number):
        """Assert that the number of messages is that expected."""
        num_msgs = len(actual_msgs)
        if num_msgs < expected_number:
            self.assertEqual(num_msgs, expected_number,
                             "Too few messages received.")
        elif num_msgs > expected_number:
            self.assertEqual(num_msgs, expected_number,
                             "Too many messages received.")

    def _assert_msgs_equal(self, actual_msgs, expected_msgs):
        """Assert that the actual and expected messages are equal.

           actual_msgs: list of message objects received
           expected_msgs: expected message strings
           """
        for msg, msg_str in zip(actual_msgs, expected_msgs):
            self.assertEqual(str(msg), msg_str)
        self._assert_msgs_length(actual_msgs, len(expected_msgs))

    def _assert_msgs_match(self, actual_msgs, expected):
        """Assert that the actual messages match the expected regular
           expression patterns.

           actual_msgs: list of message objects received
           expected: expected patterns
           """
        for msg, pattern in zip(actual_msgs, expected):
            self.assertTrue(re.match(pattern, str(msg)), "Message did match pattern %r: %s" % (pattern, msg))
        self._assert_msgs_length(actual_msgs, len(expected))

    def _assert_msgs_like(self, actual_msgs, expected):
        """Assert that the actual messages start and end with
           the expected strings.

           actual_msgs: list of message objects received
           expected_msgs: tuples of (expected_prefix, expected_suffix)
           """
        for msg, (prefix, suffix) in zip(actual_msgs, expected):
            str_msg = str(msg)

            if prefix and not str_msg.startswith(prefix):
                self.assertEqual(str_msg, prefix,
                    msg="Message '%s' does not start with '%s'."
                    % (str_msg, prefix)
                )

            if suffix and not str_msg.endswith(suffix):
                self.assertEqual(str_msg, suffix,
                    msg="Message '%s' does not end with '%s'."
                    % (str_msg, suffix)
                )
        self._assert_msgs_length(actual_msgs, len(expected))

    def _check_request_params(self, request, returns=None, raises=None):
        sock = ""
        requestname = request.__name__[8:].replace("_", "-")
        if returns is None:
            returns = []
        if raises is None:
            raises = []

        returned_msgs = [(request(sock, Message.request(requestname, *tuple(params))), expected) for (params, expected) in returns]

        msgs_equal = [(msg, expected) for (msg, expected) in returned_msgs if not hasattr(expected, "__iter__")]
        msgs_like = [(msg, expected) for (msg, expected) in returned_msgs if hasattr(expected, "__iter__")]

        if msgs_equal:
            self._assert_msgs_equal(*zip(*msgs_equal))
        if msgs_like:
            self._assert_msgs_like(*zip(*msgs_like))

        for params in raises:
            self.assertRaises(FailReply, request, sock, Message.request(requestname, *tuple(params)))

    def _assert_sensors_equal(self, get_sensor_method, sensor_tuples):
        sensor_tuples = [t + (None,)*(4-len(t)) for t in sensor_tuples]
        for sensorname, sensortype, expected, places in sensor_tuples:
            try:
                if sensortype == bool:
                    self.assertEqual(bool(int(get_sensor_method(sensorname))), expected)
                elif sensortype == float:
                    if places is not None:
                        self.assertAlmostEqual(float(get_sensor_method(sensorname)), expected, places)
                    else:
                        self.assertAlmostEqual(float(get_sensor_method(sensorname)), expected)
                else:
                    self.assertEqual(sensortype(get_sensor_method(sensorname)), expected)
            except AssertionError, e:
                raise AssertionError("Sensor %s: %s" % (sensorname, e))

    def _assert_sensors_not_equal(self, get_sensor_method, sensor_tuples):
        sensor_tuples = [t + (None,)*(4-len(t)) for t in sensor_tuples]
        for sensorname, sensortype, expected, places in sensor_tuples:
            try:
                if sensortype == bool:
                    self.assertNotEqual(bool(int(get_sensor_method(sensorname))), expected)
                elif sensortype == float:
                    if places is not None:
                        self.assertNotAlmostEqual(float(get_sensor_method(sensorname)), expected, places)
                    else:
                        self.assertNotAlmostEqual(float(get_sensor_method(sensorname)), expected)
                else:
                    self.assertNotEqual(sensortype(get_sensor_method(sensorname)), expected)
            except AssertionError, e:
                raise AssertionError("Sensor %s: %s" % (sensorname, e))

    def _wait_until_sensor_equals(self, timeout, get_sensor_method, sensorname, sensortype, value, places=7):
        stoptime = time.time() + timeout
        success = False

        if sensortype == bool:
            cmpfun = lambda got, exp: bool(int(got)) == exp
        elif sensortype == float:
            cmpfun = lambda got, exp: abs(float(got)-exp) < 10**-places
        else:
            cmpfun = lambda got, exp: sensortype(got) == exp

        while time.time() < stoptime:
            if cmpfun(get_sensor_method(sensorname), value):
                success = True
                break
            time.sleep(0.1)

        if not success:
            self.fail("Timed out while waiting %ss for %s sensor to become %s." % (timeout, sensorname, value))

def device_wrapper(device):
    outgoing_informs = []

    def reply_inform(sock, msg, orig_msg):
        outgoing_informs.append(msg)

    def inform(sock, msg):
        outgoing_informs.append(msg)

    def mass_inform(msg):
        outgoing_informs.append(msg)

    def informs():
        return outgoing_informs

    def clear_informs():
        del outgoing_informs[:]

    device.inform = inform
    device.reply_inform = reply_inform
    device.mass_inform = mass_inform
    device.informs = informs
    device.clear_informs = clear_informs

    return device
