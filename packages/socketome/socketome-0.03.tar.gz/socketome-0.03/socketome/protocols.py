class Protocol(object):
    def __init__(self, so):
        self.so = so
    def on_recv_data(self, so): pass
    def on_send_data(self, so): pass


class LineProtocol(Protocol):
    def on_recv_data(self, so):
        lines  = so.input_buffer.split('\n')
        so.input_buffer = lines.pop()
        for line in lines:
            if line[-1] == '\r': line = line[:-1]
            self.line_received(line)

    def line_received(self, line): raise NotImplementedError

    def send_line(self, line):
        self.so.output_buffer += line + '\n'
        
