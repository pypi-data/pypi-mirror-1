import os.path, sqlite3, urllib2, urlparse, uuid

class Cache:
	def __init__(self, cacheDir, dbName):
		self.__cacheDir = cacheDir
		
		#create or open a database (DB)
		conn = sqlite3.connect(cacheDir + "/" + dbName)
		conn.isolation_level = None #auto commit
		self.__c = conn.cursor()
		
		#search tables in DB
		self.__c.execute("""select * from sqlite_master""")
		row = self.__c.fetchall() 
		
		#if no tables create "cache"
		if len(row) == 0:
			self.__c.execute("""create table cache(id text primary key,
				url text unique, status text, date timestamp)""")
	
	def getFile(self, url):
		"""get a file from URL or from cache"""
		return self.__cacheDir + "/" + self.__download(url)
	
	def getModule(self, url):
		"""get a module from URL or from cache"""
		filename = self.__download(url)
		ext = os.path.splitext(filename)
		exec "import %s as mod" % ext[0]
		return mod
		
	def __download(self, url):
		path = urlparse.urlparse(url)[2]
		ext = os.path.splitext(path)
		
		#self.__c.execute("""delete from cache""")
		
		#search URL in cache
		self.__c.execute("""select * from cache where url = ?""", (url,))
		row = self.__c.fetchall() 
		
		#if no URL download and put in cache database and folder
		if len(row) == 0:
					
			print "downloading " + url
			web = urllib2.urlopen(url)
			file = web.read()

			#generate ID
			id = "a" + str(uuid.uuid1()).replace("-", "")
			
			#put file in folder
			filename = id + ext[1]
			filepath = self.__cacheDir + "/" + filename
			f = open(filepath, "wb")
			f.write(file)
			f.close()
			
			#put URL in database
			self.__c.execute("""insert into cache(id, url, status, date)
				values(?, ?, 'downloaded', strftime('%Y-%m-%d %H:%M:%f','now'))""", (id,url))

			print "downloaded as " + filename
		
		else:
		
			#get file from folder
			id = row[0][0]
			filename = id + ext[1]
			print "get " + url
			print "from cache " + filename
		
		return filename
