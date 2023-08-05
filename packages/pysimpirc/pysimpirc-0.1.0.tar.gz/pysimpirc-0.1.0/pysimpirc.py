""" Simple IRC module
"""

import re
from socket import socket, AF_INET6, AF_INET, SOCK_STREAM
from select import select

from token_bucket import TokenBucketBuffer

class IRCError(BaseException):
    """ Base class for all IRC related exceptions.
    """

class InvalidIRCData(IRCError):
    """ Raised when the passed data wasn't parsed because of structural
        invalidation.
    """

class Disconnected(IRCError):
    """ Raised when the socket is disconnected.
    """

class ModeArgumentError(IRCError):
    """ Raised when an invalid number of arguments was passed to a mode
        function.
    """

class IRCHostmask(object):
    """Rerepsents a normal hostmask."""

    def __init__(self, from_mask=None):
        self.nickname = None
        self.username = None
        self.hostname = None
        if from_mask:
            self.parse(from_mask)

    def parse(self, mask):
        self.nickname, rest = (mask + "!").split("!")[:2]
        if rest:
            self.username, rest = (rest + "@").split("@")[:2]
            self.hostname = rest
    
    def __str__(self):
        r = self.nickname
        if self.username:
            r += "!" + self.username
            if self.hostname:
                r += "@" + self.hostname
        return r

    def __repr__(self):
        return "IRCHostmask(%r)" % str(self)

    def __hash__(self):
        return hash(str(self))

    def __cmp__(self, o):
        return cmp(str(self), o)

class IRCConnection(object):
    """ Main IRC connection, subclassable.
    """

    use_ipv6 = False
    irc_line_prefixed = re.compile(r'^:([^ ]+) (.*)$')
    irc_line_unprefixed = re.compile(r'^([^ ]+)(?: (.*))?$')

    def __init__(self, remote_address=None, nickname=None, username=None,
            password=None, realname=None, local_address=None):
        """ Construct an IRCConnection object.

            server_address must be a tuple of format (addr, port).
            nickname, username and realname are for convenience with
            IRCConnection.register.
        """

        self.process = False
        self.nickname = nickname
        self.username = username
        self.password = password
        self.realname = realname
        self.socket = socket((AF_INET, AF_INET6)[int(self.use_ipv6)], SOCK_STREAM)
        if local_address:
            self.socket.bind(local_address)
        self.out_tbb = TokenBucketBuffer(
            max_size=3,
            regen_amount=0.5,
            callback=self.socket.send)
        self.in_buffer = ""
        self.socket.connect(remote_address)

    def __getattribute__(self, attrname):
        try:
            return object.__getattribute__(self, attrname)
        except AttributeError:
            if attrname.startswith("irc_"):
                return lambda self, *a: None
            else:
                raise
    
    def register(self):
        """ Convenience function for sending registration data.
        """

        self.send("NICK :%s\n" % (self.nickname,))
        self.send("USER %s 0 0 :%s\n" % (self.username, self.realname))
        if self.password is not None:
            self.send("PASS :%s\n" % (self.password,))
    
    def send(self, data):
        r""" Queues the given data, waiting for the TBB to give it a go.

        Notice that this converts \r and \r\n to just \n.
        """
        for line in data.replace("\r", "").split("\n"):
            if len(line) > 512:
                raise InvalidIRCData(line)
            elif line:
                self.debug("<<< " + line)
                self.out_tbb.append(line + "\n")

    def parse(self, line):
        """ Parse an IRC line.
            
            Requires an instance with irc_line_unprefixed and
            irc_line_prefixed set.
        """

        prefix = None
        trailing = None
        args = []

        if line.startswith(":"):
            mo = self.irc_line_prefixed.match(line)
            if not mo:
                raise InvalidIRCData(line)
            prefix, line = mo.group(1, 2)

        mo = self.irc_line_unprefixed.match(line)
        if not mo:
            raise InvalidIRCData(line)
        command, args_raw = mo.group(1, 2)
        if " :" in args_raw:
            args_raw, trailing = args_raw.split(" :", 1)
        elif args_raw.startswith(":"):
            trailing = args_raw[1:]
            args_raw = None
        if args_raw:
            args.extend(args_raw.split(" "))
        if trailing is not None:
            args.append(trailing)
        return prefix, command, args

    def process_once(self):
        """ Reads one line and processes it.

            Subclasses should call this method, since it responds to basic
            commands such as pong.
        """

        # Do the tick before so that scheduled data may be sent, and the
        # chance of receiving something will increase.
        self.out_tbb.tick()
        r, w, x = select([self.socket], [], [], 0.25)

        if r:
            recv = self.socket.recv(1024)
            if not recv:
                raise Disconnected()
            lines = (self.in_buffer + 
                recv.replace("\r\n", "\n").replace("\r", "\n")).split("\n")
            # The last "line" will have no delimiter, if it does, there's
            # another item and that'll be empty. So this is neat.
            self.in_buffer = lines.pop()

            for line in lines:
                if not line:
                    continue  # Empty lines are to be ignored.

                # Any and all EOLs are gone by now.
                self.debug(">>> " + line)
                prefix, command, arguments = self.parse(line)

                attrname = 'irc_' + command.lower()
                hostmask = IRCHostmask(prefix)
                for cls in self.__class__.mro():
                    if attrname in cls.__dict__:
                        cls.__dict__[attrname](self, hostmask, arguments)

    def process_forever(self):
        """ Process as long as self.process is True, meaning you can abort
            execution by setting process to False.
        """
        self.process = True
        while self.process:
            self.process_once()

    def debug_print(self, text):
        print text
    debug = debug_print

class CommonIRCConnection(IRCConnection):
    """ Defines a lot of convenience functions.
    """

    def _generic_target(self, command, target, message, split_lines=False):
        if split_lines:
            while message:
                # Assume command + target + 3 < 512.
                line = "%s %s :%s" % (command, target, message)
                message = line[510:]  # No \r\n.
                line = line[:510]
                self.send(line)
        else:
            self.send("%s %s :%s" % (command, target, message))

    def privmsg(self, target, message, split_lines=True):
        self._generic_target("PRIVMSG", target, message, split_lines)
    message = say = privmsg

    def notice(self, target, message, split_lines=False):
        self._generic_target("NOTICE", target, message, split_lines)

    def join(self, channels):
        self.send("JOIN %s" % (",".join(channels),))

    def nick(self, new_nickname):
        self.send("NICK :%s" % (nickname,))

    def quit(self, message=None):
        if message is not None:
            self.send("QUIT :%s" % (message,))
        else:
            self.send("QUIT")

    def set_channel_modes(self, channel, modes, args=()):
        if any(c in " \r\n\0" for arg in args for c in arg):
            raise ModeArgumentError("argument may not contain any of %r" %
                " \r\n\0")
        if hasattr(self, "aric_modes"):
            n_args = 0
            parsed_modes = []
            for mode in modes:
                if mode in self.aric_modes:
                    n_args += 1
                    if n_args > len(args):
                        raise ModeArgumentError("too few arguments")
                    parsed_modes.append((mode, args[n_args - 1]))
                else:
                    parsed_modes.append((mode, None))
            max_modes = getattr(self, "max_modes", 6)
            while parsed_modes:
                parsed_modes = parsed_modes[:max_modes]
                self.send("MODE %s %s %s" % (channel,
                    "".join(i[0] for i in parsed_modes),
                    " ".join(i[1] for i in parsed_modes if i[1] is not None)))
                parsed_modes = parsed_modes[max_modes:]
        else:
            self.send("MODE %s %s %s" % (channel, modes, " ".join(args)))

    # Callbacks
    def irc_ping(self, prefix, (text,)):
        self.send("PONG :%s" % (text,))

    def irc_nick(self, prefix, (new_nickname,)):
        if self.nickname == prefix.nickname:
            self.nickname = new_nickname
            if hasattr(self, "on_own_nick_change"):
                self.on_own_nick_change(prefix.nickname, new_nickname)

    def irc_005(self, prefix, args):
        args = args[1:-1]  # Slice off pesky text with no useful meaning.
        # TODO: Move self.server_address init to __init__? Maybe a good idea
        # unless of course a server sends no 005, in which case it'll look
        # like it doesn't support anything at all.
        self.server_support = getattr(self, "server_support", {})
        for arg in args:
            if "=" in arg:
                self.server_support.update(dict((arg.split("=", 1),)))
            else:
                self.server_support[arg] = True
        if "CHANMODES" in self.server_support and \
                self.server_support["CHANMODES"].count(",") == 3:
            (list_modes, param_modes, param_when_set,
                inaric_modes) = self.server_support["CHANMODES"].split(",")
            self.aric_modes = list_modes + param_modes + param_when_set
            self.inaric_modes = inaric_modes
        if "PREFIX" in self.server_support:
            prefixes = self.server_support["PREFIX"]
            if prefixes.startswith("(") and ")" in prefixes:
                modes, signs = prefixes[1:].split(")", 1)
                if len(modes) == len(signs):
                    self.mode_sign_map = dict(zip(modes, signs))
                self.aric_modes = getattr(self, "aric_modes", "") + modes
        if "MODES" in self.server_support:
            try:
                self.max_modes = int(self.server_support["MODES"])
            except ValueError:
                pass

if __name__ == '__main__':
    server = raw_input("Server: ")
    nickname = raw_input("Nickname: ")
    username = raw_input("Username: ")
    realname = raw_input("Realname: ")
    
    m = IRCConnection((server, 6667), nickname, username, realname)
    m.register()
    m.process_forever()
