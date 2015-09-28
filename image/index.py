#!/usr/bin/python
# -*- coding:utf-8 -*-

from qiniu import *
from Queue import Queue
from logging.config import fileConfig
import pymysql, hashlib, threading, random, sys, json, time, logging

logging.basicConfig(
	level=logging.DEBUG,
	format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
	datefmt='%a, %d %b %Y %H:%M:%S',
	filename='migrate.log',
	filemode='w'
)

class qiniu_thread(threading.Thread):
	def __init__(self, queue, config, access_key, secret_key, bucket_name):
		self.qauth = None
		self.bucket = None
		self.data = queue
		self.config = config
		self.access_key = access_key
		self.secret_key = secret_key
		self.bucket_name = bucket_name
		threading.Thread.__init__(self)

	def run(self):
		self.connect()
		print("ready to fetch file...")
		time.sleep(3)
		while True:
			if self.data.qsize() > 0:
				data = json.loads(self.data.get())
				url = "http://jue.so/UpLoad/WorksPhoto/%s/%s" % (data["TopId"], data["ImgPath"])
				
				fetch_info = self.fetch(url)
				if fetch_info != None:
					move_info = self.move(url, fetch_info["hash"])

					file_info = data.copy()
					file_info.update(fetch_info)
					self.put_data(file_info)
			else:
				break

	def get_qauth(self):
		if self.qauth == None:
			self.qauth = Auth(self.access_key, self.secret_key)
		return self.qauth

	def get_bucket(self):
		if self.bucket == None:
			self.bucket = BucketManager(self.get_qauth())
		return self.bucket

	def delete(self, url):
		bucket = self.get_bucket()
		info, ret = bucket.delete(self.bucket_name, hashlib.md5(url).hexdigest())
		if ret.status_code == 200:
			logging.info("delete: %s" % hashlib.md5(url).hexdigest())
		else:
			logging.error("error delete: %s" % hashlib.md5(url).hexdigest())

	def fetch(self, url):
		bucket = self.get_bucket()
		info, ret = bucket.fetch(url, self.bucket_name, hashlib.md5(url).hexdigest())
		if ret.status_code == 200:
			return info
		else:
			logging.error("error fetch: %s" %  hashlib.md5(url).hexdigest())

	def move(self, url, fname):
		bucket = self.get_bucket()
		info, ret = bucket.move(self.bucket_name, hashlib.md5(url).hexdigest(), self.bucket_name, fname)
		if ret.status_code == 200:
			return info
		elif ret.status_code == 614:
			logging.info("exist: %s" %  hashlib.md5(url).hexdigest())
			self.delete(url)
		else:
			logging.error("error move: %s" %  hashlib.md5(url).hexdigest())

	def put_data(self, file_info):
		if self.local_conn == None:
			self.connect()
		cursor = self.local_conn.cursor()
		sql = "INSERT INTO `PicFile` (`id`, `ImgPath`, `ImgExt`, `UserId`, `TopId`, `md5`, `hash`, `size`, `mimeType`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
		value = (file_info["Id"], file_info["ImgPath"], file_info["ImgExt"], file_info["UserId"], file_info["TopId"], file_info["key"], file_info["hash"], file_info["fsize"], file_info["mimeType"])
		cursor.execute(sql, value)
		self.local_conn.commit()
		
	def connect(self):
		config = self.config
		self.local_conn = pymysql.connect(host=config["host"], port=config["port"], user=config["user"], passwd=config["pass"], db=config["db"], cursorclass=pymysql.cursors.DictCursor)
		return self.local_conn

class sql_thread(threading.Thread):
	def __init__(self, queue, config):
		self.data = queue
		self.config = config
		threading.Thread.__init__(self)
	
	def run(self):
		offset = 0
		limit = 100
		self.connect()
		print("ready to get data...")

		while True:
			if self.data.qsize() < limit:
				print("offset -> %s" % offset)
				self.get_data(limit, offset)
				offset = offset + limit
			if offset >= 22871:
				print("game over, success...")
				break

	def get_data(self, limit, offset):
		if self.jue_conn == None:
			self.connect()

		cursor = self.jue_conn.cursor()
		sql = "SELECT `ImgExt`, `Id`, `TopId`, `ImgPath`, `UserId` FROM `jue_works_pic` WHERE 1 LIMIT %s, %s"
		cursor.execute(sql, (offset, limit))
		for row in cursor:
			self.data.put(json.dumps(row))
			
	def connect(self):
		config = self.config
		self.jue_conn = pymysql.connect(host=config["host"], port=config["port"], user=config["user"], passwd=config["pass"], db=config["db"], cursorclass=pymysql.cursors.DictCursor)
		return self.jue_conn

def main():
	'''qiniu.com access_key, secret_key'''
	access_key = ""
	secret_key = ""
	bucket_name = ""

	jue_config = {
		"host": "127.0.0.1",
		"port": 3306,
		"user": "user",
		"pass": "pass",
		"db": "database"
	}

	local_config = {
		"host": "127.0.0.1",
		"port": 3306,
		"user": "user",
		"pass": "pass",
		"db": "migrate"
	}

	queue = Queue()
	producer = sql_thread(queue, jue_config)
	consumer = qiniu_thread(queue, local_config, access_key, secret_key, bucket_name)

	producer.start()
	consumer.start()
	producer.join()
	consumer.join()

if __name__ == "__main__":
	main()
