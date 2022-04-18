import asyncio
import websockets
import socket
import json

# temporarily storing api keys here
# don't forget to change this later
keys = {
    "123" : ""
}

class AuthServer():
    def __init__(self):
        self.commands = {
            "auth" : self.auth,
            "reg" : self.reg,
            "id" : self.id
        }

        self.accountData = {}
        
        with open("account_data.json", "r") as accounts:
            try:
                self.accountData = json.load(accounts)
            except:
                pass

    async def start(self): 
        ip = socket.gethostbyname(socket.gethostname())
        port = 5050
        print(f"[STARTING] authentication server has started")
        print(f"[LISTENING] listening on port {port}")

        async with websockets.serve(self.handle_connection, ip, port):
            await asyncio.Future()

    async def handle_connection(self, websocket):
        addr = websocket.remote_address[0]
        print(f"[ATTEMPTING CONNECTION] {addr} is attempting to connect")
        print(f"[VALIDATING] awaiting a valid key from {addr}")

        message = await websocket.recv()
        if message not in keys:
            print(f"[VALIDATION FAILED] provided api key does not match any stored")
            print(f"[CLOSING] closing connection to {addr}")
            websocket.close()
            return
        
        print(f"[VALIDATED] validation successful")
        await self.main_loop(websocket)

    async def main_loop(self, websocket):
        while True:
            command = await websocket.recv()
            command = await self.parse_command(command)
            await self.execute_command(command)

    async def write_to_account_db(self):
        with open("account_data.json", "w") as accounts:
            json.dump(self.accountData, accounts)

    async def parse_command(self, command):
        parsed = {
            "method" : "",
            "args": []
        }

        methodParsed = False
        delimiter = "|"
        curr = ""
        for char in command:
            if char == delimiter and methodParsed == False:
                curr = curr.strip()
                parsed["method"] = curr
                curr = ""
                methodParsed = True
            elif char == delimiter:
                parsed["args"].append(curr)
                curr = ""
            else:
                curr += char

        parsed["args"].append(curr)
        return parsed

    async def execute_command(self, command):
        method = self.commands[command["method"]]
        await method(*command["args"])
    
    async def auth(self, *args):
        username = args[0]
        passHash = args[1]

        if username not in self.accountData:
            print("account not in database")
            return -1

        if passHash != self.accountData[username]:
            print("does not match")
            return 1

        print("matches")
        return 0
            
    async def reg(self, *args):
        username = args[0]
        passHash = args[1]

        if username in self.accountData:
            print("name taken")
            return 1
        
        self.accountData[username] = passHash
        print("registered")
        await self.write_to_account_db()

        return 0
    
    async def id(self, *args):
        pass
    
        
        

server = AuthServer()

asyncio.run(server.start())