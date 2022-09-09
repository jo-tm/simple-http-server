#!/usr/bin/env python3
"""
Very simple HTTP server in python for logging requests
Usage::
    ./server.py [<port>]
"""
from http.server import BaseHTTPRequestHandler, HTTPServer
import logging, json, time

import json
from web3 import Web3

## Strategy api-spot example request
example_req = '''
{
  "options":     {
        "api": "https://test-url.for-snapshot.com:8000",
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

mass_delegate_req = '''
{
  "network": "1",
  "delegator": "0xdededededededededededededededededededede",
  "delegatees": [
        {
            "address" : "0xdededededededededededededededededededede",
            "weight" : "95"
        },
        {
            "address" : "0xd649bACfF66f1C85618c5376ee4F38e43eE53b63",
            "weight" : "1"
        },
        {
            "address" : "0xEA2E9cEcDFF8bbfF107a349aDB9Ad0bd7b08a7B7",
            "weight" : "1"
        },
        {
            "address" : "0x3c4B8C52Ed4c29eE402D9c91FfAe1Db2BAdd228D",
            "weight" : "1"
        },
        {
            "address" : "0x726022a9fe1322fA9590FB244b8164936bB00489",
            "weight" : "1"
        },
        {
            "address" : "0xc6665eb39d2106fb1DBE54bf19190F82FD535c19",
            "weight" : "1"
        }
  ],
  "total_weight" : "100",
  "snapshot": 11437846,
  "permit" : "SIGNATURE TO BE INCLUDED"
}
'''

myabi = '''[{"constant":true,"inputs":[],"name":"mintingFinished","outputs":[{"name":"","type":"bool"}],"payable":false,"type":"function"},{"constant":true,"inputs":[],"name":"name","outputs":[{"name":"","type":"string"}],"payable":false,"type":"function"},{"constant":false,"inputs":[{"name":"_spender","type":"address"},{"name":"_value","type":"uint256"}],"name":"approve","outputs":[],"payable":false,"type":"function"},{"constant":true,"inputs":[],"name":"totalSupply","outputs":[{"name":"","type":"uint256"}],"payable":false,"type":"function"},{"constant":false,"inputs":[{"name":"_from","type":"address"},{"name":"_to","type":"address"},{"name":"_value","type":"uint256"}],"name":"transferFrom","outputs":[],"payable":false,"type":"function"},{"constant":true,"inputs":[],"name":"decimals","outputs":[{"name":"","type":"uint256"}],"payable":false,"type":"function"},{"constant":false,"inputs":[],"name":"unpause","outputs":[{"name":"","type":"bool"}],"payable":false,"type":"function"},{"constant":false,"inputs":[{"name":"_to","type":"address"},{"name":"_amount","type":"uint256"}],"name":"mint","outputs":[{"name":"","type":"bool"}],"payable":false,"type":"function"},{"constant":true,"inputs":[],"name":"paused","outputs":[{"name":"","type":"bool"}],"payable":false,"type":"function"},{"constant":true,"inputs":[{"name":"_owner","type":"address"}],"name":"balanceOf","outputs":[{"name":"balance","type":"uint256"}],"payable":false,"type":"function"},{"constant":false,"inputs":[],"name":"finishMinting","outputs":[{"name":"","type":"bool"}],"payable":false,"type":"function"},{"constant":false,"inputs":[],"name":"pause","outputs":[{"name":"","type":"bool"}],"payable":false,"type":"function"},{"constant":true,"inputs":[],"name":"owner","outputs":[{"name":"","type":"address"}],"payable":false,"type":"function"},{"constant":true,"inputs":[],"name":"symbol","outputs":[{"name":"","type":"string"}],"payable":false,"type":"function"},{"constant":false,"inputs":[{"name":"_to","type":"address"},{"name":"_value","type":"uint256"}],"name":"transfer","outputs":[],"payable":false,"type":"function"},{"constant":false,"inputs":[{"name":"_to","type":"address"},{"name":"_amount","type":"uint256"},{"name":"_releaseTime","type":"uint256"}],"name":"mintTimelocked","outputs":[{"name":"","type":"address"}],"payable":false,"type":"function"},{"constant":true,"inputs":[{"name":"_owner","type":"address"},{"name":"_spender","type":"address"}],"name":"allowance","outputs":[{"name":"remaining","type":"uint256"}],"payable":false,"type":"function"},{"constant":false,"inputs":[{"name":"newOwner","type":"address"}],"name":"transferOwnership","outputs":[],"payable":false,"type":"function"},{"anonymous":false,"inputs":[{"indexed":true,"name":"to","type":"address"},{"indexed":false,"name":"value","type":"uint256"}],"name":"Mint","type":"event"},{"anonymous":false,"inputs":[],"name":"MintFinished","type":"event"},{"anonymous":false,"inputs":[],"name":"Pause","type":"event"},{"anonymous":false,"inputs":[],"name":"Unpause","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"name":"owner","type":"address"},{"indexed":true,"name":"spender","type":"address"},{"indexed":false,"name":"value","type":"uint256"}],"name":"Approval","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"name":"from","type":"address"},{"indexed":true,"name":"to","type":"address"},{"indexed":false,"name":"value","type":"uint256"}],"name":"Transfer","type":"event"}]'''
infura_url = "https://rinkeby.infura.io/v3/890b63f3265f4331ae435bef1c0869b8"
web3 = Web3(Web3.HTTPProvider(infura_url))
abi=json.loads(myabi)
# MINT contract
contract_address = "0xa63C6E2Af9c87768f741E1BB7f77511d23152C7B"
contract = web3.eth.contract(address=contract_address, abi=abi)
totalSupply = contract.functions.totalSupply().call()
#print(totalSupply)
#print(contract.functions.name().call())
#print(contract.functions.symbol().call())

def balance_of_erc20(addr):
    address2 = Web3.toChecksumAddress(addr)
    # use getPriorVotes() for BIT token
    # function getPriorVotes(address account, uint256 blockNumber) public view returns (uint256)
    balance = contract.functions.balanceOf(address2).call()
    #print(balance)
    int_balance = (balance) // 10**18
    #print(int_balance)
    return int_balance

# cache
_balance_of = {}

def voting_power(addr):
    bal = None
    # use cache only for 2 minutes
    if addr in _balance_of and time.time() - _balance_of[addr][1] < 120.0: 
        bal = _balance_of[addr][0]
    else:
        bal = balance_of_erc20(addr)
        _balance_of[addr] = (bal, time.time())
    return bal


# 1. UserA has 10,000 MINT
# 2. UserB has 5,000 MINT
# 3. UserA make a proposal PropA.
# 4. UserA votes YES and UserB votes NO on PropA. Win YES
# 5. UserA does mass-delegation with weight 6 self-delegate and 4 mass delegate to UserB.
# 6. UserA has net voting power 6,000 MINT.
# 7. UserB has net voting power 9,000 MINT
# 8. UserA make a proposal PropB.
# 9. UserA votes YES and UserB votes NO on PropA. Win No.
# 10. UserA does mass-delegation with weight 1 self-delegate.
# 8. UserA make a proposal PropC.
# 9. UserA votes YES and UserB votes NO on PropA. Win YES.


class S(BaseHTTPRequestHandler):

    _delegators = {}
    _delegatees = {}
    _balance_of = {}

    def _set_response(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET(self):
        logging.info("GET request,\nPath: %s\nHeaders:\n%s\n", str(self.path), str(self.headers))
        self._set_response()
        self.wfile.write("GET request for {}".format(self.path).encode('utf-8'))


    def verify_total_weight(self, obj):
        assert( int(obj['total_weight']) == float(obj['total_weight']) )
        total = int(obj['total_weight'])
        sum_w = 0
        for d in obj['delegatees']:
            assert( int(d['weight']) == float(d['weight']) )
            sum_w += int(d['weight'])
        assert( total == sum_w )


    def update_mass_delegate(self, obj):
        delegator = obj['delegator']
        block_number = obj["snapshot"]
        #TODO: check signature from permit, signer=delegator
        prev_list = []
        num_delegatees = 0
        if not delegator in self._delegators:
            self._delegators[delegator] = []
        else: # prev list
            prev_list = [dic['address'] for dic in self._delegators[delegator][-1]['delegatees'] ]
        self.verify_total_weight(obj)
        total_weight = int(obj['total_weight'])
        self._delegators[delegator].append( obj )

        for delegatee in obj['delegatees']:
            delegatee_addr = delegatee['address']
            if not delegatee_addr in self._delegatees:
                self._delegatees[delegatee_addr] = []
            # block_number, delegator address, delegatee weight
            self._delegatees[delegatee_addr].append((block_number,delegator,int(delegatee['weight']),total_weight))
            num_delegatees += 1
        # missing delegatees from prev list must get zero weight.
        for prev_delegatee in prev_list:
            self._delegatees[prev_delegatee].append((block_number,delegator,0,total_weight))
        return num_delegatees, delegator


    def get_checkpoint(self, list_obj, block_number):

        if list_obj[-1]['snapshot'] < block_number:
            return list_obj[-1] #len(list_obj) - 1
        assert( len(list_obj) > 1 )

        ret_val = None
        for i in range(len(list_obj)-1):
            if list_obj[i]['snapshot'] < block_number and list_obj[i+1]['snapshot'] > block_number:
                ret_val = list_obj[i]
        assert( ret_val != None)
        return ret_val


    def net_voting_power(self, addr, block_number):
        token_balance = voting_power(addr
        )
        # has someone delegated to to addr?
        is_delegatee = False
        if addr in self._delegatees: #len(self._delegatees[addr]) > 0: # and self._delegatees[addr][-1][2] > 0:
            is_delegatee = True

        # is delegator?
        # is_delegator overrides is_delegatee
        is_delegator = addr in self._delegators #len(self._delegators[addr]) > 0

        if is_delegator:
            list_obj = self._delegators[addr]
            checkpoint_obj = self.get_checkpoint(list_obj, block_number)
            total_weight = int(checkpoint_obj['total_weight'])
            self_weight = 0
            dl = [d for d in checkpoint_obj['delegatees'] if addr==d['address']]
            if len(dl) > 0: # has self mass-delegated weight
                self_weight = int(dl[0]['weight'])
            net_balance = self_weight * token_balance // total_weight
            return net_balance

        if is_delegatee:
            delegated_weight = self._delegatees[addr][-1][2]
            total_weight = self._delegatees[addr][-1][3]
            delegator = self._delegatees[addr][-1][1]
            delegator_balance = voting_power(delegator)
            # delegatee balance + fraction of delegated balance
            token_balance += delegated_weight * delegator_balance // total_weight
        
        return token_balance


    def do_POST(self):
        content_length = int(self.headers['Content-Length']) # <--- Gets the size of data
        post_data = self.rfile.read(content_length) # <--- Gets the data itself
        logging.info("POST request,\nPath: %s\nHeaders:\n%s\n\nBody:\n%s\n",
                str(self.path), str(self.headers), post_data.decode('utf-8'))

        #post_data = example_req
        print(post_data)
        obj = json.loads(post_data)

        response = {}
        if self.path == "/voting-power":
            response["score"] = []
            block_number = obj['snapshot']
            for addr in obj['addresses']:
                response["score"].append( {"address" : addr, "score" : self.net_voting_power(addr,block_number)} )
        elif self.path == "/mass-delegate":
            num_delegatees, delegator = self.update_mass_delegate(obj)
            response = { 'status' : 'ok', 'delegator' : delegator, 'number_of_delegatees' : str(num_delegatees)  }

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
