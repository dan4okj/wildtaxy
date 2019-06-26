import asyncio

HOST = '127.0.0.1'
PORT = 12000
PACKET_SIZE = 4096

class EchoServerProtocol(asyncio.Protocol):

	def connection_made(self, transport):
		peername = transport.get_extra_info('peername')
		print("Connection from", peername)
		self.transport = transport

	def data_received(self, data):
		msg = data.decode()
		print("Data Received", msg)

		self.transport.write(data)
		print('Send', data)

		print('Closing connection socket')
		self.transport.close()

class ProxyServerProtocol(asyncio.Protocol):

	def connection_made(self, transport):
		peername = transport.get_extra_info('peername')
		print("(proxy) Connection from", peername)
		self.transport = transport

	def data_received(self, data):
		msg = data.decode()
		print("(proxy) Data Received", msg)

	#	print(self.transport)
	#	self.transport.write(data)
	#	print('Send', data)

		await self.send_to_echo(data)

		print('Closing connection socket')
		self.transport.close()

	async def send_to_echo(data):

		try:
			e_reader, e_writer = asyncio.open_connection(HOST, 12001)

			e_writer.write(data)
		#	while not e_reader.at_eof():
		finally:
			e_reader.close()
			e.writer.close()


async def handle_connection(reader, writer):
	while True:
		data = await reader.read(PACKET_SIZE)
		if not data:
			break

		writer.write(data)
		await writer.drain()

	writer.close()


#syncio.run(wild_taxy_server(HOST, 12001))
def start():

	loop = asyncio.get_event_loop()
	proxy_coro = loop.create_server(ProxyServerProtocol, HOST, PORT)
	echo_coro = loop.create_server(EchoServerProtocol, HOST, 12001)
	# Get the server up and running
	proxy_server = loop.run_until_complete(proxy_coro)
	print('Server running on', proxy_server.sockets[0].getsockname())

	echo_server = loop.run_until_complete(echo_coro)
	print('Server running on', echo_server.sockets[0].getsockname())

	try:
		loop.run_forever()
	except KeyboardInterrupt:
		print("Interrupted, shutting down server")

	#Close socket
	proxy_server.close()

	loop.run_until_complete(poxy_server.wait_closed())
	loop.close()

#asyncio.run(start())
start()
