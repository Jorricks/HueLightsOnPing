import threading
from flask import Flask, jsonify, send_from_directory, request, redirect, url_for
from werkzeug.serving import make_server


class WebConfig:
    def __init__(self, host, port, enter_perm_off, enter_perm_on, enter_ping):
        self.st = ServerThread(host, port, enter_perm_off, enter_perm_on, enter_ping)

    def start_web_servers(self):
        try:
            self.st.start()
        except:
            print('The webserver config thread ran into an error')
            self.shutdown_web_servers()
            self.st.shutdown_server()
            self.st.join()

    def shutdown_web_servers(self):
        print('Shutting down the webservers')
        self.st.shutdown_server()
        self.st.join()


class ServerThread(threading.Thread):
    def __init__(self, host, port, enter_perm_off, enter_perm_on, enter_ping, *args, **kwargs):
        super(ServerThread, self).__init__(*args, **kwargs)
        self.host = host
        self.port = port
        self.enter_perm_off = enter_perm_off
        self.enter_perm_on = enter_perm_on
        self.enter_ping = enter_ping
        self.shutdown_fun = self.run
        self.srv = ''

    def run(self):  # Do the actual work.
        app = Flask(__name__)

        lights_permanently_off = self.enter_perm_off
        lights_permanently_on = self.enter_perm_on
        lights_ping = self.enter_ping

        @app.route('/perm/on')
        def permanent_on():
            lights_permanently_on()
            return jsonify({'data': 'Success'})

        @app.route('/perm/off')
        def permanent_off():
            lights_permanently_off()
            return jsonify({'data': 'Success'})

        @app.route('/ping')
        def switch_to_ping():
            lights_ping()
            return jsonify({'data': 'Success'})

        print('Starting webserver')
        try:
            self.srv = make_server(self.host, self.port, app)
            print('Started webserver at {}:{}'.format(self.host, self.port))
        except OSError as e:
            print('Error starting webserver at {}:{}'.format(self.host, self.port))
            print('{}'.format(e))
        if __name__ == 'webcomponent':
            self.srv.serve_forever()
        else:
            print('Error, __name__ is "{}"'.format(__name__))

    def shutdown_server(self):
        self.srv.shutdown()
