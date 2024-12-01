# coding=utf-8
# References:
# * https://github.com/devsnek/discord-rpc/tree/master/src/transports/IPC.js
# * https://github.com/devsnek/discord-rpc/tree/master/example/main.js
# * https://github.com/discordapp/discord-rpc/tree/master/documentation/hard-mode.md
# * https://github.com/discordapp/discord-rpc/tree/master/src
# * https://discordapp.com/developers/docs/rich-presence/how-to#updating-presence-update-presence-payload-fields

import json
import os
import socket
import struct
import sys
import time
import uuid
from abc import ABCMeta, abstractmethod

from logger import logger

OP_HANDSHAKE = 0
OP_FRAME = 1
OP_CLOSE = 2
OP_PING = 3
OP_PONG = 4


class DiscordIpcError(Exception):
    pass


class DiscordIpcClient(metaclass=ABCMeta):
    """Work with an open Discord instance via its JSON IPC for its rich presence API.

    In a blocking way.
    Classmethod `for_platform`
    will resolve to one of WinDiscordIpcClient or UnixDiscordIpcClient,
    depending on the current platform.
    Supports context handler protocol.
    """

    def __init__(self, client_id):
        try:
            self.client_id = client_id
            self.connection_established = False
            self.connection_attempts = 0  # Counter for connection attempts(if the connection is broken/lost even if Discord is open)
            self._connect_and_handshake()
        except Exception as e:
            self.connection_established = False
            logger.error(f'{e}')

    def _connect_and_handshake(self):
        try:
            self._connect()
            if not hasattr(self, '_f') or self._f is None:
                raise DiscordIpcError("Failed to initialize connection: Discord pipe not available.")
            self._do_handshake()
            self.connection_established = True
        except Exception:
            self.connection_established = False
            raise DiscordIpcError("Couldn't initialize connection to Discord. Make sure Discord is running.")

    @classmethod
    def for_platform(cls, client_id, platform=sys.platform):
        if platform == 'win32':
            return WinDiscordIpcClient(client_id)
        else:
            return UnixDiscordIpcClient(client_id)

    @abstractmethod
    def _connect(self):
        pass

    def _do_handshake(self):
        try:
            ret_op, ret_data = self.send_recv({'v': 1, 'client_id': self.client_id}, op=OP_HANDSHAKE)
            # {'cmd': 'DISPATCH', 'data': {'v': 1, 'config': {...}}, 'evt': 'READY', 'nonce': None}
            if ret_op == OP_FRAME and ret_data['cmd'] == 'DISPATCH' and ret_data['evt'] == 'READY':
                return
            else:
                if ret_op == OP_CLOSE:
                    self.close()
                return RuntimeError(ret_data)
        except Exception as e:
            self.connection_established = False
            raise DiscordIpcError(f"Handshake failed: {str(e)}")

    @abstractmethod
    def _write(self, date: bytes):
        pass

    @abstractmethod
    def _recv(self, size: int) -> bytes:
        pass

    def _recv_header(self) -> (int, int):
        header = self._recv_exactly(8)
        return struct.unpack("<II", header)

    def _recv_exactly(self, size) -> bytes:
        buf = b""
        size_remaining = size
        while size_remaining:
            chunk = self._recv(size_remaining)
            buf += chunk
            size_remaining -= len(chunk)
        return buf

    def close(self):
        try:
            self.send({}, op=OP_CLOSE)
        finally:
            self._close()

    @abstractmethod
    def _close(self):
        pass

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()

    def send_recv(self, data, op=OP_FRAME):
        self.send(data, op)
        return self.recv()

    def send(self, data: dict, op=OP_FRAME):
        try:
            data_str = json.dumps(data, separators=(',', ':'))
            data_bytes = data_str.encode('utf-8')
            header = struct.pack("<II", op, len(data_bytes))
            self._write(header)
            self._write(data_bytes)
        except Exception as e:
            self.connection_established = False

    def recv(self) -> (int, "JSON"):
        """Receives a packet from discord.

        Returns op code and payload.
        """
        op, length = self._recv_header()
        payload = self._recv_exactly(length)
        data = json.loads(payload.decode('utf-8'))
        return op, data

    reconnect_notification = False  # So it doesnt log the reconnect message multiple times
    discord_open_notification = False  # So it doesnt log the discord not open message multiple times

    # Edited from pypresence for convenience(https://github.com/qwertyquerty/pypresence/blob/master/pypresence/presence.py)
    def set_activity(self, state=None, details=None, start=None, large_image=None, large_text=None,
                     small_image=None, small_text=None):
        """Set activity for the user, reconnecting only if Discord is open."""
        if not self._is_discord_open():
            if not self.discord_open_notification:
                logger.error("Discord is not running. Please open Discord and try again.")
                self.discord_open_notification = True
            return

        # delay(0.5)  # Added to add a delay as too fast breaks the presence update
        # Even if connection boolean is set to true, it may not be connected if an error occurs so make sure to check connection_attempts
        if self.connection_attempts >= 3:
            if not self.reconnect_notification:
                logger.error(
                    "Failed to connect to Discord after multiple attempts. Please use 'discord' command in cheat console to reconnect.")
                self.reconnect_notification = True
            return

        try:
            if not self.connection_established:
                self._connect_and_handshake()  # Attempt to reconnect if connection isn't established

            data = {
                "cmd": 'SET_ACTIVITY',
                "args": {
                    "pid": os.getpid(),
                    "activity": {
                        "state": state,
                        "details": details,
                        "timestamps": {
                            "start": start,
                        },
                        "assets": {
                            "large_image": large_image,
                            "large_text": large_text,
                            "small_image": small_image,
                            "small_text": small_text
                        },
                    },
                },
                "nonce": str(uuid.uuid4())
            }
            self.send(remove_none(data))  # Attempt to send the activity data
            self.connection_attempts = 0  # Reset connection attempts after successful activity
        except OSError as e:
            logger.error(
                "Discord is not initialized correctly." if e.errno == 22 else f"Unexpected OSError during activity update: {str(e)}")
            self.connection_established = False
            self.connection_attempts += 1
        except Exception as e:
            logger.error(f"Unexpected error while setting activity: {str(e)}")
            self.connection_established = False
            self.connection_attempts += 1

    def check_connection(self):
        pass

    def _is_discord_open(self):
        """Check if Discord is running without fully initializing the connection."""
        try:
            pipe_pattern = self._get_pipe_pattern() if hasattr(self, '_get_pipe_pattern') else self._pipe_pattern
            for i in range(10):
                path = pipe_pattern.format(i)
                if os.path.exists(path):  # If the pipe exists, Discord is open
                    return True
            return False
        except Exception as e:
            print(f"Error checking if Discord is open: {e}")
            return False


# Taken from pypresence(https://github.com/qwertyquerty/pypresence/blob/master/pypresence/utils.py)
def remove_none(d: dict):  # Made by https://github.com/LewdNeko ;^)
    for item in d.copy():
        if isinstance(d[item], dict):
            if len(d[item]):
                d[item] = remove_none(d[item])
            else:
                del d[item]
        elif d[item] is None:
            del d[item]
    return d


class WinDiscordIpcClient(DiscordIpcClient):
    _pipe_pattern = r'\\?\pipe\discord-ipc-{}'

    def _connect(self):
        for i in range(10):
            path = self._pipe_pattern.format(i)
            try:
                self._f = open(path, "w+b")
                self.path = path
                break
            except OSError as e:
                pass
        else:
            return DiscordIpcError("Failed to connect to Discord pipe")

        self.path = path

    def _write(self, data: bytes):
        self._f.write(data)
        self._f.flush()

    def _recv(self, size: int) -> bytes:
        return self._f.read(size)

    def _close(self):
        self._f.close()


class UnixDiscordIpcClient(DiscordIpcClient):

    def _connect(self):
        self._sock = socket.socket(socket.AF_UNIX)
        pipe_pattern = self._get_pipe_pattern()

        for i in range(10):
            path = pipe_pattern.format(i)
            if not os.path.exists(path):
                continue
            try:
                self._sock.connect(path)
            except OSError as e:
                pass
            else:
                break
        else:
            return DiscordIpcError("Failed to connect to Discord pipe")

    @staticmethod
    def _get_pipe_pattern():
        env_keys = ('XDG_RUNTIME_DIR', 'TMPDIR', 'TMP', 'TEMP')
        for env_key in env_keys:
            dir_path = os.environ.get(env_key)
            if dir_path:
                break
        else:
            dir_path = '/tmp'
        return os.path.join(dir_path, 'discord-ipc-{}')

    def _write(self, data: bytes):
        self._sock.sendall(data)

    def _recv(self, size: int) -> bytes:
        return self._sock.recv(size)

    def _close(self):
        self._sock.close()


def delay(seconds):
    start_time = time.time()
    while time.time() - start_time < seconds:
        pass
