from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import re

class Client:
    def __init__(self, id, name, balance):  # Используйте __init__ для конструктора
        self.id = id
        self.name = name
        self.balance = balance

class BankRepository:
    def __init__(self):
        self.clients = []
        self.next_id = 1  # Добавьте атрибут next_id в конструктор

    def create_client(self, name, balance):
        new_client = Client(self.next_id, name, balance)
        self.clients.append(new_client)
        self.next_id += 1
        return new_client

    def read_client(self, client_id):
        for client in self.clients:
            if client.id == client_id:
                return client
        return None

    def delete_client(self, client_id):
        for client in self.clients:
            if client.id == client_id:
                self.clients.remove(client)
                return True
        return False

    def list_clients(self):
        return self.clients

    def filter_clients(self, parameter, value):
        filtered_clients = []
        if parameter == 'id':
            filtered_clients = [client for client in self.clients if str(client.id) == value]
        elif parameter == 'name':
            filtered_clients = [client for client in self.clients if value.lower() in client.name.lower()]
        elif parameter == 'balance':
            filtered_clients = [client for client in self.clients if str(client.balance) == value]
        elif parameter == 'name_approx':  
            filtered_clients = [client for client in self.clients if value.lower() in client.name.lower()]
        return filtered_clients

bank_repository = BankRepository()
client1 = bank_repository.create_client("alice", 1000)
client2 = bank_repository.create_client("Andrey", 30000)
client3 = bank_repository.create_client("Stanislav",15000)
client4 = bank_repository.create_client("Timofey", 20000)
client5 = bank_repository.create_client("Nikita", 10000)
client6 = bank_repository.create_client("Dima", 15000)
client7 = bank_repository.create_client("Sasha", 13000)
client8 = bank_repository.create_client("Dasha", 14000)
client9 = bank_repository.create_client("Vanya", 12000)
client10 = bank_repository.create_client("Egor", 16000)
class SimpleAPI(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path == '/clients':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data)
            
            if 'name' not in data or 'balance' not in data or not data['name'] or not data['balance']:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b'Name and balance cannot be empty')
                return
    
            client = bank_repository.create_client(data['name'], data['balance'])
            self.send_response(201)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"id": client.id, "name": client.name, "balance": client.balance}).encode())
    def do_PUT(self):
        if self.path.startswith('/clients/'):
            client_id = int(self.path.split('/')[-1])
            content_length = int(self.headers['Content-Length'])
            put_data = self.rfile.read(content_length)
            data = json.loads(put_data)
            client = bank_repository.read_client(client_id)
        if client:
            if 'name' in data:
                client.name = data['name']
            if 'balance' in data:
                client.balance = data['balance']
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"id": client.id, "name": client.name, "balance": client.balance}).encode())
        else:
            self.send_response(404)
            self.end_headers()
        if 'name' not in data or 'balance' not in data or not data['name'] or not data['balance']:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b'Name and balance cannot be empty')
                return

    
    def do_DELETE(self):
        if self.path.startswith('/clients/'):
            client_id = int(self.path.split('/')[-1])
            if bank_repository.delete_client(client_id):
                self.send_response(204)
                self.end_headers()
            else:
                self.send_response(404)
                self.end_headers()

    def do_GET(self):
        if self.path == '/clients':
            self.list_clients()
        elif re.match(r'/clients/\d+', self.path):
            client_id = int(re.search(r'\d+', self.path).group())
            self.get_client(client_id)
        elif self.path.startswith('/clients/filter'):
            parameter = self.path.split('=')[1].split('&')[0]
            value = self.path.split('=')[2]
            self.filter_clients(parameter, value)
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'Not found')

    def list_clients(self):
        clients = bank_repository.list_clients()
        client_list = [{"id": client.id, "name": client.name, "balance": client.balance} for client in clients]
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(client_list).encode())

    def get_client(self, client_id):
        client = bank_repository.read_client(client_id)
        if client:
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"id": client.id, "name": client.name, "balance": client.balance}).encode())
        else:
            self.send_response(404)
            self.end_headers()

    def filter_clients(self, parameter, value):
        filtered_clients = bank_repository.filter_clients(parameter, value)
        client_list = [{"id": client.id, "name": client.name, "balance": client.balance} for client in filtered_clients]
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(client_list).encode())
    
if __name__ == '__main__':
    server_address = ('', 8000)
    httpd = HTTPServer(server_address, SimpleAPI)
    print('Starting server on http://localhost:8000...')
    httpd.serve_forever()
