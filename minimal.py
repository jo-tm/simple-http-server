#!/usr/bin/env python3
"""
Very simple HTTP server in python for logging requests
Usage::
    ./server.py [<port>]
"""
from http.server import BaseHTTPRequestHandler, HTTPServer
import logging, json, time, urllib.parse

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
  "content": {
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
    "snapshot": 11437846
  }, 
  "permit" : "SIGNATURE TO BE INCLUDED"
}
'''

example_form = '''<!DOCTYPE html>
<html>
<body>

<h1>Mass Delegation - Functional Prototype (Rinkeby)</h1>

<p>Using COMP-like Rinkeby Test Token TBIT
(<a href="https://rinkeby.etherscan.io/address/0xcb198597184804f175dc7b562b0b5af0793e9176#writeContract">Execute test token TBIT comp-delegation and unrestricted minting here</a>)</p>
<p>Test mass-delegated TBIT on Snapshot (<a href="https://demo.snapshot.org/#/playground/api-post?query=eyJwYXJhbXMiOnsiYXBpIjoiaHR0cDovLzM0LjIyMC4xMTguMjE6ODAwMC92b3RpbmctcG93ZXIiLCJzeW1ib2wiOiJUQklUIiwiZGVjaW1hbHMiOjB9LCJuZXR3b3JrIjoiNCIsInNuYXBzaG90IjoiIiwiYWRkcmVzc2VzIjpbIjB4RUEyRTljRWNERkY4YmJmRjEwN2EzNDlhREI5QWQwYmQ3YjA4YTdCNyIsIjB4M2M0QjhDNTJFZDRjMjllRTQwMkQ5YzkxRmZBZTFEYjJCQWRkMjI4RCIsIjB4ZDY0OWJBQ2ZGNjZmMUM4NTYxOGM1Mzc2ZWU0RjM4ZTQzZUU1M2I2MyIsIjB4NzI2MDIyYTlmZTEzMjJmQTk1OTBGQjI0NGI4MTY0OTM2YkIwMDQ4OSIsIjB4YzY2NjVlYjM5ZDIxMDZmYjFEQkU1NGJmMTkxOTBGODJGRDUzNWMxOSIsIjB4NmVmMjM3NmZhNmUxMmRhYmIzYTNlZDBmYjQ0ZTRmZjI5ODQ3YWY2OCJdfQ..">Demo Snapshot Voting Power playground for TBIT here</a>)</p>
<p>Create new Test Proposals (<a href="https://demo.snapshot.org/#/bitdao-test.eth/">Demo Snapshot Proposals Homepage here</a>)</p>



<form action="/mass-delegate-form">
  <p><label for="w3review">Submit to mass-delegate voting power:</label></p>
  <label for="fname">Delegator address:</label>
  <input type="text" id="delegator" name="delegator"><br>
  <em>Note: only comp-delegated voting power can be mass-delegated.</em><br>
  <br>
  <label for="fname">Block number:</label>
  <input type="text" id="blockNumber" name="blockNumber"><br>
  <em>Note: leave empty for current block number.</em><br><br>
  <label for="fname">CSV (address,weight):</label><br>
  <em>Note: only checksum addresses.</em><br>
  <textarea id="delegatees" name="delegatees" rows="32" cols="50">
0x287c1b65992aAC3Ff67aDE9FeB9F3A73289E7277,5
0x4F6b3B68Fde374aA0B14967E52CF3443Af5Dd3a5,3
0xA78905e37CE42CE51D906b7A277363993Abb4598,2
  </textarea>
  <br>
  <input type="submit" value="Submit">
</form>

<p>
<b>WARNING: just for validation and exploration, Not A Production Ready Implementation!</b>
</p>

</body>
</html>
'''

myabi = '''[{"inputs":[{"internalType":"address","name":"_admin","type":"address"}],"stateMutability":"nonpayable","type":"constructor"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"owner","type":"address"},{"indexed":true,"internalType":"address","name":"spender","type":"address"},{"indexed":false,"internalType":"uint256","name":"value","type":"uint256"}],"name":"Approval","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"delegator","type":"address"},{"indexed":true,"internalType":"address","name":"fromDelegate","type":"address"},{"indexed":true,"internalType":"address","name":"toDelegate","type":"address"}],"name":"DelegateChanged","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"delegate","type":"address"},{"indexed":false,"internalType":"uint256","name":"previousBalance","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"newBalance","type":"uint256"}],"name":"DelegateVotesChanged","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"oldAdmin","type":"address"},{"indexed":true,"internalType":"address","name":"newAdmin","type":"address"}],"name":"NewAdmin","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"oldPendingAdmin","type":"address"},{"indexed":true,"internalType":"address","name":"newPendingAdmin","type":"address"}],"name":"NewPendingAdmin","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"uint256","name":"id","type":"uint256"}],"name":"Snapshot","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"from","type":"address"},{"indexed":true,"internalType":"address","name":"to","type":"address"},{"indexed":false,"internalType":"uint256","name":"value","type":"uint256"}],"name":"Transfer","type":"event"},{"inputs":[],"name":"DELEGATION_TYPEHASH","outputs":[{"internalType":"bytes32","name":"","type":"bytes32"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"DOMAIN_TYPEHASH","outputs":[{"internalType":"bytes32","name":"","type":"bytes32"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"MAX_SUPPLY","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"acceptAdmin","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"admin","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"owner","type":"address"},{"internalType":"address","name":"spender","type":"address"}],"name":"allowance","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"spender","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"approve","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"account","type":"address"}],"name":"balanceOf","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"account","type":"address"},{"internalType":"uint256","name":"snapshotId","type":"uint256"}],"name":"balanceOfAt","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"","type":"address"},{"internalType":"uint256","name":"","type":"uint256"}],"name":"checkpoints","outputs":[{"internalType":"uint256","name":"fromBlock","type":"uint256"},{"internalType":"uint256","name":"votes","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"decimals","outputs":[{"internalType":"uint8","name":"","type":"uint8"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"spender","type":"address"},{"internalType":"uint256","name":"subtractedValue","type":"uint256"}],"name":"decreaseAllowance","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"delegatee","type":"address"}],"name":"delegate","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"delegatee","type":"address"},{"internalType":"uint256","name":"nonce","type":"uint256"},{"internalType":"uint256","name":"expiry","type":"uint256"},{"internalType":"uint8","name":"v","type":"uint8"},{"internalType":"bytes32","name":"r","type":"bytes32"},{"internalType":"bytes32","name":"s","type":"bytes32"}],"name":"delegateBySig","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"","type":"address"}],"name":"delegates","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"account","type":"address"}],"name":"getCurrentVotes","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"account","type":"address"},{"internalType":"uint256","name":"blockNumber","type":"uint256"}],"name":"getPriorVotes","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"spender","type":"address"},{"internalType":"uint256","name":"addedValue","type":"uint256"}],"name":"increaseAllowance","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"account","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"mint","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"name","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"","type":"address"}],"name":"nonces","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"","type":"address"}],"name":"numCheckpoints","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"pendingAdmin","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"newPendingAdmin","type":"address"}],"name":"setPendingAdmin","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"snapshot","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"symbol","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"totalSupply","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"snapshotId","type":"uint256"}],"name":"totalSupplyAt","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"recipient","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"transfer","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"sender","type":"address"},{"internalType":"address","name":"recipient","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"transferFrom","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"nonpayable","type":"function"}]'''
infura_url = "https://rinkeby.infura.io/v3/890b63f3265f4331ae435bef1c0869b8"
web3 = Web3(Web3.HTTPProvider(infura_url))
abi=json.loads(myabi)
# MINT contract
contract_address = "0xCB198597184804f175Dc7b562b0b5AF0793e9176"
contract = web3.eth.contract(address=contract_address, abi=abi)

def current_block_number():
    return int(web3.eth.block_number)

def balance_of_erc20(addr):
    address2 = Web3.toChecksumAddress(addr)
    # use getPriorVotes() for BIT token
    # function getPriorVotes(address account, uint256 blockNumber) public view returns (uint256)
    balance = contract.functions.balanceOf(address2).call()
    int_balance = (balance) // 10**18
    return int_balance

def delegated_votes_prior(addr, block_number):
    address2 = Web3.toChecksumAddress(addr)
    # use getPriorVotes() for BIT token
    # function getPriorVotes(address account, uint256 blockNumber) public view returns (uint256)
    votes = contract.functions.getPriorVotes(addr, block_number ).call()
    int_votes = (votes) // 10**18
    return int_votes

# cache
_balance_of = {}

def voting_power(addr, block_number):
    bal = None
    # use cache only for 15 seconds
    if addr in _balance_of and time.time() - _balance_of[addr][1] < 15.0: 
        bal = _balance_of[addr][0]
    else:
        bal = delegated_votes_prior(addr, block_number)
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

#0x287c1b65992aAC3Ff67aDE9FeB9F3A73289E7277,5
#0x4F6b3B68Fde374aA0B14967E52CF3443Af5Dd3a5,3
#0xA78905e37CE42CE51D906b7A277363993Abb4598,2

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
        path_s = self.path.split('?')
        if path_s[0] == '/mass-delegate-form': # do mass-delegate
            # url decode form in the path
            # ?delegator=0x666&blockNumber=12345&delegatees=0xcafecafeafe%2C6%0D%0A0xaaaaaaaaaaa%2C4
            url_str = '?'.join(path_s[1:])
            print('URL STR: ' + url_str)
            obj = urllib.parse.parse_qs(url_str)
            print(obj)
            assert( 'delegator' in obj )
            assert( len(obj['delegator']) == 1 )
            obj['delegator'] = obj['delegator'][0]
            if not 'blockNumber' in obj or len(obj['blockNumber']) == 0 or obj['blockNumber'] == ['']:
                obj['snapshot'] = current_block_number()
            else:
                obj['snapshot'] = int(obj['blockNumber'][0])
            assert( len(obj['delegatees']) == 1 )
            total_weight = 0
            delegatees = []
            for delegatee_l in obj['delegatees'][0].strip().split('\n'):
                delegatee_l = delegatee_l.strip()
                ds_s = delegatee_l.split(',')
                assert( len(ds_s) == 2)
                total_weight += int(ds_s[1])
                assert( int(ds_s[1]) > 0)
                d_dict = {'address':ds_s[0], 'weight': str(ds_s[1]) }
                delegatees.append( d_dict )
            obj['delegatees'] = delegatees
            obj['total_weight'] = str(total_weight)
            # Execute
            self.update_mass_delegate(obj)
            self.wfile.write(example_form.replace('<!--/>','<script>alert("MASS DELEGATED COMPLETED!")</script>').encode('utf-8'))
        else:
            self.wfile.write(example_form.encode('utf-8'))

        #self.wfile.write("GET request for {}".format(self.path).encode('utf-8'))


    def verify_total_weight(self, obj):
        assert( int(obj['total_weight']) == float(obj['total_weight']) )
        total = int(obj['total_weight'])
        sum_w = 0
        for d in obj['delegatees']:
            assert( int(d['weight']) > 0 and int(d['weight']) == float(d['weight']) )
            sum_w += int(d['weight'])
        assert( total == sum_w )


    def update_mass_delegate(self, obj):
        delegator = obj['delegator']
        if not 'snapshot' in obj:
            block_number = current_block_number()
        else:
            block_number = obj['snapshot']
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
        return num_delegatees, delegator, block_number


    def get_checkpoint(self, list_obj, block_number):
        if len(list_obj) == 0:
            return None

        if list_obj[-1]['snapshot'] < block_number:
            return list_obj[-1] #len(list_obj) - 1
        if len(list_obj) == 1:
            return None

        ret_val = None
        for i in range(len(list_obj)-1):
            j = len(list_obj) - 2 - i
            if list_obj[j]['snapshot'] < block_number and list_obj[i+1]['snapshot'] > block_number:
                ret_val = list_obj[j]
        return ret_val


    def net_voting_power(self, addr, block_number):
        token_balance = voting_power(addr, block_number)
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
            if checkpoint_obj:
                total_weight = int(checkpoint_obj['total_weight'])
                self_weight = 0
                dl = [d for d in checkpoint_obj['delegatees'] if addr==d['address']]
                if len(dl) > 0: # has self mass-delegated weight
                    self_weight = int(dl[0]['weight'])
                net_balance = self_weight * token_balance // total_weight
                return net_balance
            else:
                return token_balance

        if is_delegatee:
            delegated_weight = self._delegatees[addr][-1][2]
            total_weight = self._delegatees[addr][-1][3]
            delegator = self._delegatees[addr][-1][1]
            delegator_balance = voting_power(delegator, block_number)
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
            if not 'snapshot' in obj:
                block_number = current_block_number()
            else:
                block_number = obj['snapshot']
            for addr in obj['addresses']:
                response["score"].append( {"address" : addr, "score" : self.net_voting_power(addr,block_number)} )
        elif self.path == "/mass-delegate":
            obj = obj['content']
            num_delegatees, delegator, block_number = self.update_mass_delegate(obj)
            response = { 'status' : 'ok', 'block_number': int(block_number), 'delegator' : delegator, 'number_of_delegatees' : str(num_delegatees)  }

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
