import sqlite3
import sys
import time
import os

class GPSRecorder:
	DB_NAME = 'gps.db'
	INTERVAL_SECONDS = 30
	DEBUG = True

	def __init__(self):
		if sys.platform == 'linux-armv7l':
			import androidhelper
			self._droid = androidhelper.Android()
			self._droid.startLocating()
			os.chdir('/storage/emulated/0/qpython')
		else:
			#Mock gps call
			class MockDroid:
				def getLatestLocation(self):
					return 

				def readLocation(self):
					class Result:
						result = {'gps': {'latitude': 1, 'longitude': 2}}
					return Result()

			self._droid = MockDroid()

	def connect(self):
		conn = sqlite3.connect(self.DB_NAME)
		self._cursor = conn.cursor()

	def is_positions_table(self):
		self._cursor.execute("SELECT count(*) FROM sqlite_master WHERE type='table' AND name='Positions'")
		exists, = self._cursor.fetchone()
		return exists

	def setup_db(self):
		if not self.is_positions_table():
			self._cursor.execute("CREATE TABLE Positions(Id INTEGER PRIMARY KEY, Timestamp BIGINT, Latitude FLOAT, Longitude FLOAT);")

	def add_gps_location(self, latitude, longitude):
		timestamp_integer = int(time.time())
		query = "INSERT INTO Positions(Timestamp, Latitude, Longitude) VALUES({}, {}, {})".format(timestamp_integer, latitude, longitude)
		self._cursor.execute(query)

	def get_gps_locations(self):
		query = "SELECT * FROM Positions"
		self._cursor.execute(query)
		rows = self._cursor.fetchall()

		locations = []
		for row in rows:
			locations.append({'id': row[0], 'timestamp': row[1], 
				'latitude': row[2], 'longitude': row[3]})

		return locations

	def getLocation(self):
		location = self._droid.readLocation().result
		if 'gps' in location:
			return location['gps']
		else:
			return None

	def check(self, elapsed):
		"""Check if we need to record GPS"""
		if elapsed > self.INTERVAL_SECONDS:
			#Record GPS
			android_location = self.getLocation()
			if android_location:
				self.add_gps_location(android_location['latitude'], android_location['longitude'])
			else:
				print('No location available')
			return True
		else:
			return False
			
	def run(self):
		print('Start gps recording')
		previous_time = time.time()
		while True:
			current_time = time.time()
			elapsed = current_time - previous_time

			if self.check(elapsed):
				previous_time = current_time
				if self.DEBUG:
					print(len(self.get_gps_locations()))

			time.sleep(1)

if __name__ == '__main__':
	recorder = GPSRecorder()
	recorder.connect()
	recorder.setup_db()

	recorder.INTERVAL_SECONDS = 2
	recorder.run()
