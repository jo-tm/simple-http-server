#!/usr/bin/env python3
"""
Very simple HTTP server in python for logging requests
Usage::
    ./server.py [<port>]
"""
from http.server import BaseHTTPRequestHandler, HTTPServer
import logging, json

## Strategy api-spot example request
example_req = '''
{
  "options":     {
        "api": "https://dao-staging.polychainmonsters.com/v1/votingPowerTestMock",
        "symbol": "BIT",
        "decimals": 0
        },
  "network": "1",
  "addresses": [
    "0xEA2E9cEcDFF8bbfF107a349aDB9Ad0bd7b08a7B7",
    "0x3c4B8C52Ed4c29eE402D9c91FfAe1Db2BAdd228D",
    "0xd649bACfF66f1C85618c5376ee4F38e43eE53b63",
    "0x726022a9fe1322fA9590FB244b8164936bB00489",
    "0xc6665eb39d2106fb1DBE54bf19190F82FD535c19",
    "0x6ef2376fa6e12dabb3a3ed0fb44e4ff29847af68"
  ],
  "snapshot": 11437846
}
'''

example_resp = '''{
  "score": [
    {
      "address": "0xed2bcc3104da5f5f8fa988d6e9fafd74ae62f319",
      "score": 166
    },
    {
      "address": "0x94150ae78d562f58b60cb783c7b7ab1ca7c438cc",
      "score": 123
    },
    {
      "address": "0x2f14a4abc940049de389973c8d4ad022712dafc6",
      "score": 106
    },
    '''
response = {
  "score": []
}

class S(BaseHTTPRequestHandler):
    def _set_response(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET(self):
        logging.info("GET request,\nPath: %s\nHeaders:\n%s\n", str(self.path), str(self.headers))
        self._set_response()
        self.wfile.write("GET request for {}".format(self.path).encode('utf-8'))

    def do_POST(self):
        content_length = int(self.headers['Content-Length']) # <--- Gets the size of data
        post_data = self.rfile.read(content_length) # <--- Gets the data itself
        logging.info("POST request,\nPath: %s\nHeaders:\n%s\n\nBody:\n%s\n",
                str(self.path), str(self.headers), post_data.decode('utf-8'))

        #post_data = example_req
        print(post_data)
        obj = json.loads(post_data)
        response["score"] = []
        for addr in obj['addresses']:
            response["score"].append( {"address" : addr, "score" : "60"} )

        self._set_response()
        self.wfile.write(json.dumps(response, indent=4).encode('utf-8'))
        #self.wfile.write("POST request for {}".format(self.path).encode('utf-8'))

def run(server_class=HTTPServer, handler_class=S, port=8000):
    logging.basicConfig(level=logging.INFO)
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    logging.info('Starting httpd...\n')
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    logging.info('Stopping httpd...\n')

if __name__ == '__main__':
    from sys import argv

    if len(argv) == 2:
        run(port=int(argv[1]))
    else:
        run()
