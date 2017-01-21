import json,httplib,urllib

class ListenAppAPI(object):

	# TODO set these values
	APPLICATION_ID = ""
	REST_API_KEY = ""
	USERNAME = ""
	PASSWORD = ""
	LISTEN_APP_PARSE_SERVER_URL = "listen-app-parse-server.herokuapp.com"

	def __init__(self):
		super(ListenAppAPI, self).__init__()
		self.connection = httplib.HTTPSConnection(ListenAppAPI.LISTEN_APP_PARSE_SERVER_URL, 443)
		self.session_token = "" # TODO is this initializing even required here?

	def updateChannelState(self, channel):
		try:
			channel_id = self._fetchChannelID(channel.id)
			self._login()
			self._updateChannelState(channel_id, channel.state)
			self._logout()
		except ListenAppAPIError as error:
			print(error.message)
			print(error.jsonResponse)
			raise # TODO whats the correct thing to do here?

	def _login(self):
		params = urllib.urlencode({ "username": ListenAppAPI.USERNAME, "password": ListenAppAPI.PASSWORD })
		self.connection.connect()
		self.connection.request('GET', '/parse/login?%s' % params, '', {
			   "X-Parse-Application-Id": ListenAppAPI.APPLICATION_ID,
			   "X-Parse-REST-API-Key": ListenAppAPI.REST_API_KEY,
			   "X-Parse-Revocable-Session": "1"
			 })
		result = json.loads(self.connection.getresponse().read())
		try:
			self.session_token = result["sessionToken"] # save session token	
		except KeyError as e:
			raise ListenAppAPIError("Could not login", result)

	def _logout(self):
		self.connection.connect()
		self.connection.request('POST', '/parse/logout', '', {
			   "X-Parse-Application-Id": ListenAppAPI.APPLICATION_ID,
			   "X-Parse-REST-API-Key": ListenAppAPI.REST_API_KEY,
			   "X-Parse-Session-Token": self.session_token
			 })
		result = json.loads(self.connection.getresponse().read())
		# {} as response here is expected. If something else is returned it did not work correctly
		if len(result) > 0:
			raise ListenAppAPIError("Could not logout correctly", result)

	def _fetchChannelID(self, channel_id):
		# only match channels with xenim as streaming backend
		# and the correct matchingId
		params = urllib.urlencode({"where":json.dumps({
			   "streamingBackend": "xenim",
			   "matchingId": channel_id
			 })})
		self.connection.connect()
		self.connection.request('GET', '/parse/classes/Channel?%s' % params, '', {
			   "X-Parse-Application-Id": ListenAppAPI.APPLICATION_ID,
			   "X-Parse-REST-API-Key": ListenAppAPI.REST_API_KEY
			 })
		result = json.loads(self.connection.getresponse().read())

		try:
			results = result["results"]
			if len(results) == 1:
				channel = results[0] # get the one single element of the results
				return channel["objectId"]
			else:
				raise ListenAppAPIError("Could not fetch channelId.", result)
		except KeyError as e:
			raise ListenAppAPIError("Could not fetch channelId", result)

	def _updateChannelState(self, channel_id, new_state):
		self.connection.connect()
		self.connection.request('PUT', '/parse/classes/Channel/' + channel_id, json.dumps({
			   "state": new_state
			 }), {
			   "X-Parse-Application-Id": ListenAppAPI.APPLICATION_ID,
			   "X-Parse-REST-API-Key": ListenAppAPI.REST_API_KEY,
			   "X-Parse-Session-Token": self.session_token,
			   "Content-Type": "application/json"
			 })
		result = json.loads(self.connection.getresponse().read())
		try:
			# If updating the data worked correctly, the response does contain the 'updatedAt' key
			result["updatedAt"]
		except KeyError as e:
			raise ListenAppAPIError("Could not update the channel state", result)





class Error(Exception):
	"""Base class for exceptions in this module."""
	pass

class ListenAppAPIError(Error):

	def __init__(self, message, jsonResponse):
		self.message = message
		self.jsonResponse = jsonResponse