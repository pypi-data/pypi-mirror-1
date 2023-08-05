class Term(object):

    def __init__ (self, command = None, autostart = True, pty = None):

        from os.path import expanduser

        self.command = None

        if command:

            self.command = expanduser(command).split(" ")

            while '' in self.command:
                self.command.remove('')

        self.__pid = None
        self.pty = pty
        if self.pty:
            self.pty = open(self.pty, 'r+')
            self._set_nb([self.pty.fileno()])

        self.serversocket = None

        if autostart:
            self.start()

    def start(self):

        from sys import exit
        from os import fdopen
        from pty import spawn, fork

        if self.status() in ['not running', 'killed'] and self.command and not self.pty:

            self.__pid, childid = fork()

            if self.pid == 0:
                spawn(self.command)
                exit(0)
            else:
                self.pty = fdopen(childid, 'r+')

            self._set_nb([self.pty.fileno()])

    def _get_pid(self):

        return self.__pid

    def _set_nb(self, fdlist):
        
        from os import O_NONBLOCK
        from fcntl import fcntl, F_GETFL, F_SETFL
        
        for fd in fdlist:
            fl = fcntl(fd, F_GETFL)
            fcntl(fd, F_SETFL, fl | O_NONBLOCK)

    def _write_process(self, str):
        self.pty.write(str)
        self.pty.flush()

    def _read_process(self):
        data = self.pty.read(-1)
        return data

    def _write(self, handle, str):
        
        from socket import socket

        if isinstance(handle, socket):
            size = handle.send(str)
            if size == 0:
                raise RuntimeError, (1, 'ERROR: socket connection broken')
        else:
            try:
                handle.write(str)
            except IOError, (errno, strerror):
                if errno == 11:
                    pass
                else:
                    raise
            handle.flush()
        
    def _read(self, handle, rbufsize = 4096):

        from socket import socket

        if isinstance(handle, socket):
            data = handle.recv(rbufsize)
            if len(data) == 0:
                raise RuntimeError, (1, 'ERROR: socket connection broken')
        else:
            data = handle.read(-1)
        return data

    def kill(self, signal):

        from os import kill
        
        try:
            kill(self.pid, signal)
        except OSError, (errno, strerror):
            if errno == 3:
                pass
            else:
                raise

    def wait(self):

        from os import waitpid

        try:
            waitpid(self.pid, 0)
        except OSError, (errno, strerror):
            if errno == 10:
                pass
            else:
                raise

        self.__pid = None
        self.pty = None


    def status(self):

        from os import waitpid, WNOHANG

        status = 'not running'

        if self.pid:
            try:
                waitpid(self.pid, WNOHANG)
                status = 'running'
            except OSError, (errno, strerror):
                if errno == 10:
                    status = 'killed'
        
        if self.command:
            return status
        else:
            return None

    def socket(self, host = "", port = 0):
        
        from socket import socket, AF_INET, SOCK_STREAM

        if not self.serversocket:
            self.serversocket = socket(AF_INET, SOCK_STREAM)
            self.serversocket.bind((host, port))
            self.serversocket.listen(1)
            return self.serversocket.getsockname()[1]
        else:
            return None

    def serve(self):

        from os import waitpid
        from select import select

        if not self.pty:
            return

        (clientsocket, address) = self.serversocket.accept()
        clientsocket.setblocking(0)

        connections = {clientsocket: self.pty, self.pty: clientsocket}

        while clientsocket:
            try:
                readers = select(connections.keys(), [], [])[0]
                writers = select([], connections.values(), [])[1]
                if clientsocket in readers:
                    data = self._read(clientsocket)
                    if data and connections[clientsocket] in writers:
                        self._write_process(data)
                if self.pty in readers:
                    data = self._read_process()
                    if data and connections[self.pty] in writers:
                        self._write(clientsocket, data)
                        
            except IOError, (errno, strerror):
                if errno == 5:
                    pid, status = waitpid(self.pid, 0)
                    break
                else:
                    raise
                
            except RuntimeError, (errno, strerror):
                if errno == 1:
                    break

        clientsocket.close()
        self.serversocket.close()
        self.serversocket = None

    def connect(self, host = None, port = None):

        from sys import stdin, stdout
        from fcntl import ioctl
        from struct import pack, unpack
        from termios import TIOCGWINSZ, TIOCSWINSZ
        from select import select
        from socket import socket, AF_INET, SOCK_STREAM
        from tty import setraw
        from os import waitpid
        from termios import tcgetattr, tcsetattr, TCSADRAIN, ECHO

        if not host and not port:
            if not self.command:
                raise ValueError, 'ERROR: host and port not specified'
            if not self.pty:
                raise ValueError, 'ERROR: command not started'
            handle = self.pty
        else:
            handle = socket(AF_INET, SOCK_STREAM)
            handle.connect((str(host), int(port)))
            handle.setblocking(0)

        mysize = pack("HHHH", 0, 0, 0, 0)
        lines, cols = unpack("HHHH", ioctl(stdout.fileno(), TIOCGWINSZ, mysize))[:2]

        if handle == self.pty:
            newsize = pack("HHHH", lines, cols, 0, 0)
            ioctl(handle.fileno(), TIOCSWINSZ, newsize)

        oldterm = tcgetattr(stdin)
        newterm = tcgetattr(stdin)
        newterm[3] = newterm[3] & ~ECHO
        tcsetattr(stdin.fileno(), TCSADRAIN, newterm)

        setraw(stdin.fileno())

        self._set_nb([stdin.fileno()])

        connections = {handle: stdout, stdin: handle}

        while handle:
            try:
                readers = select(connections.keys(), [], [])[0]
                writers = select([], connections.values(), [])[1]
                if handle in readers:
                    data = self._read(handle)
                    if data and connections[handle] in writers:
                        self._write(stdout, data)
                if stdin in readers:
                    data = self._read(stdin)
                    if data == '\x01':
                        select([stdin], [], [])
                        command = self._read(stdin)
                        if command == 'a':
                            self._write(handle, '\x01')
                        elif command == 'x':
                            break
                    elif data and connections[stdin] in writers:
                        self._write(handle, data)
                        
            except IOError, (errno, strerror):
                if errno == 5 and handle == self.pty:
                    try:
                        pid, status = waitpid(self.pid, 0)
                        break

                    except OSError, (errno, strerror):
                        if errno == 10:
                            break
                else:
                    raise

            except RuntimeError, (errno, strerror):
                if errno == 1:
                    break
                
            except KeyboardInterrupt:
                self._write(handle, '')

        if handle != self.pty:
            handle.close()

        tcsetattr(stdin.fileno(), TCSADRAIN, oldterm)

    pid = property(_get_pid)
