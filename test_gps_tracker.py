import unittest
import mock

import gps_recorder
import os
import time

class RecorderTest(unittest.TestCase):
	def setUp(self):
		#delete existing db before tests
		try:
			os.remove(gps_recorder.GPSRecorder.DB_NAME)
		except OSError:
			pass

	def test_create_db(self):
		recorder = gps_recorder.GPSRecorder()
		recorder.connect()

	def test_is_positions_table(self):
		recorder = gps_recorder.GPSRecorder()
		recorder.connect()

		self.assertEqual(0, recorder.is_positions_table())

		recorder.setup_db()
		self.assertEqual(1, recorder.is_positions_table())

	def test_get_gps_locations(self):
		recorder = gps_recorder.GPSRecorder()
		recorder.connect()
		recorder.setup_db()

		locations = recorder.get_gps_locations()
		self.assertEqual([], locations)

	@mock.patch('time.time')
	def test_add_gps_location(self, mock_time):
		recorder = gps_recorder.GPSRecorder()
		recorder.connect()
		recorder.setup_db()

		mock_time.return_value = 12345

		lat_long = [1.1, 2.2]
		recorder.add_gps_location(*lat_long)

		locations = recorder.get_gps_locations()
		expected_list = [{'id': 1, 'timestamp': 12345, 
			'latitude': lat_long[0], 'longitude': lat_long[1]}]
		self.assertEqual(expected_list, locations)

		recorder.add_gps_location(*lat_long)
		locations = recorder.get_gps_locations()
		expected_list.append({'id': 2, 'timestamp': 12345, 
			'latitude': lat_long[0], 'longitude': lat_long[1]})
		self.assertEqual(expected_list, locations)

	def test_check(self):
		recorder = gps_recorder.GPSRecorder()
		recorder.connect()
		recorder.setup_db()

		interval = gps_recorder.GPSRecorder.INTERVAL_SECONDS
		for elapsed in range(interval):
			self.assertFalse(recorder.check(elapsed))

		self.assertTrue(recorder.check(interval + 0.1))
		#We should have one record
		locations = recorder.get_gps_locations()
		self.assertEqual(1, len(locations))


	def test_get_location(self):
		recorder = gps_recorder.GPSRecorder()
		android_location = recorder.getLocation()
		self.assertEqual({'latitude': 1, 'longitude': 2}, android_location)
		
