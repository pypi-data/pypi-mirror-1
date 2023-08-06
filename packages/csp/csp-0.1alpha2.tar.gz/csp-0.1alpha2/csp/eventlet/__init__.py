from eventlet import api, coros, wsgi

def csp_listener((interface, port)):
    l = Listener(interface, port)
    l.listen()
    return l

class Listener(object):
    def __init__(self, interface, port):
        self.interface = interface
        self.port = port
        self.site = WsgiCSP()
        
    def listen(self):
        api.spawn(wsgi.server, api.tcp_listener((interface, port)), self.site)
        
    def accept(self):
        return self.site.accept()

class WsgiCSP(object):
      
    def __init__(self):
        self._accept_channel = coros.Channel()
        self._sessions = {}
      
      
    
        if request.method.lower() == 'post':
            request.args['d'] =[request.content.read()]
        path = request.path.rsplit('/',1)[1]
        session = None
        if path != "handshake":
            key = request.args.get("s", [None])[0]
            if key not in self.root.sessions:
                # TODO: error
                return "error! no such session."
            session = self.root.sessions[key]
            session.updateVars(request)

        # XXX: obviously change this
        request.setHeader('Access-Control-Allow-Origin','*')

        return getattr(self, "render_%s"%(path,))(session, request)
      
      
      
        form = {}
        try:
            if environ['REQUEST_METHOD'].upper() == 'POST':
                qs = environ['wsgi.input'].read()
            else:
                qs = environ['QUERY_STRING']
            for key, val in cgi.parse_qs(qs).items():
                form[key] = val[0]
        except Exception, e:
            start_response('500 internal server error', [])
            return "Invalid form input: " + str(e)
      
      

        
      
    def __call__(self, environ, start_response):
        path = environ['PATH_INFO']
        try:
            form = environ['csp.form'] = get_form(environ)
        except Exception, e:
            start_response('500 internal server error', [])
            return ""
        session = None
        if path != "/handshake":
            key = form.get("s", None)
            if key not in self._sessions:
                # TODO: error
                return self._render_request_error(self, enviorn, start_response, form)
            session = self._sessions[key]
            session.update_vars(form)
            
        f = getattr(self, 'render_' + path[1:], None)
        if not f:
            return "Error"
        f(session, environ, start_response)

    def render_comet(self, session, environ, start_response):
        return session.set_comet_request(environ, start_response)

    def render_handshake(self, session, environ, start_response):
        key = str(uuid.uuid4()).replace('-', '')
        session = CSPSession(self, key, environ)
        self.root.sessions[key] = session
        api.spawn(self._accept_channel.send, session)
        return session.render_request({"session":key}, start_response)

    def render_close(self, session, environ, start_response):
        session.close()
        return session.render_request("OK", start_response)

    def render_send(self, session, environ, start_response):
        session.read(request.args.get("d", [""])[0])
        return session.render_request("OK", start_response)

    def render_reflect(self, session, environ, start_response):
        return environ['csp.form'].get('d', '')
    
    def accept(self):
        return self._accept_channel.wait()
    
def get_form(environ):
    form = {}
    qs = environ['QUERY_STRING']
    for key, val in cgi.parse_qs(qs).items():
        form[key] = val[0]
    if environ['REQUEST_METHOD'].upper() == 'POST':
        form['d'] = environ['wsgi.input'].read()
    return form
        
def _render_request_error(msg, environ, start_response, args):
    pass

def _render_comet_error(msg, environ, start_response, args):
    pass
        
def _render_request_response(output, environ, start_response, args
        
class CSPSession(object):
  
    def __init__(self, parent, environ):
        self._recv_event = None
        self.parent = parent
        self.conn_vars = {
            "rp":"",
            "rs":"",
            "du":30,
            "is":0, # False
            "i":0,
            "ps":0,
            "p":"",
            "bp":"",
            "bs":"",
            "g":0, # False
            "se":0, # False
            "ct":"text/html"
        }
        self.update_vars(environ['csp.form'])
        
    def send(self, data):
        return len(data)
    
    def recv(self, max):
        if not self.buffer:
            self._recv_event = coros.event()
            self._recv_event.wait()
            self._recv_event = None
        if self.buffer:
            data = self.buffer[:max]
            self.buffer = self.buffer[max:]
            return data


    def update_vars(self, form):
        for key in self.permVars:
            if key in form:
                newVal = form[key]
                varType = self.permVars[key].__class__
                try:
                    typedVal = varType(newVal)
                    if key == "g" and self.request and self.permVars["g"] != typedVal:
                        self.endStream()
                    self.permVars[key] = typedVal
                    if key == "ps":
                        self.prebuffer = " "*typedVal
                except:
                    pass
        ack = request.args.get("a",["-1"])[0]
        try:
            ack = int(ack)
        except ValueError:
            ack = -1
        while self.buffer and ack >= self.buffer[0][0]:
            self.buffer.pop(0)
        if self.isClosed and not self.buffer:
            self.teardown()

    def close(self):
        pass
    
    
