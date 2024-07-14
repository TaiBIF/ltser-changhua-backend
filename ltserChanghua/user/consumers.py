import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer

class MyUserConsumer(WebsocketConsumer):
	def connect(self):
		self.email_prefix = self.scope['url_route']['kwargs']['email_prefix']
		self.email_suffix = self.scope['url_route']['kwargs']['email_suffix']
		self.email = f'{self.email_prefix}A{self.email_suffix}'

		# Join room group
		async_to_sync(self.channel_layer.group_add)(
			self.email, self.channel_name
		)

		self.accept()

	def disconnect(self, close_code):
		# Leave room group
		async_to_sync(self.channel_layer.group_discard)(
			self.email, self.channel_name
		)

	# Receive message from WebSocket
	def receive(self, text_data):
		data = json.loads(text_data)
		message = data['message']

		# Send message to room group
		async_to_sync(self.channel_layer.group_send)(
			self.email, {
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