import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer

class MyUserConsumer(WebsocketConsumer):
	def connect(self):
		self.username = self.scope['url_route']['kwargs']['username']

		# Join room group
		async_to_sync(self.channel_layer.group_add)(
			self.username, self.channel_name
		)

		self.accept()

	def disconnect(self, close_code):
		# Leave room group
		async_to_sync(self.channel_layer.group_discard)(
			self.username, self.channel_name
		)

	# Receive message from WebSocket
	def receive(self, text_data):
		data = json.loads(text_data)
		message = data['message']

		# Send message to room group
		async_to_sync(self.channel_layer.group_send)(
			self.username, {
				'type': 'user_message',
				'message': message
			}
		)

	# Receive message from room group
	def user_message(self, event):
		message = event['message']

		# Send message to WebSocket
		self.send(text_data=json.dumps({
			'message': message
		}))