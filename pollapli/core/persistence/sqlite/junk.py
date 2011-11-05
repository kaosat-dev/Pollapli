
    @defer.inlineCallbacks
    def _generateMasterDatabase(self):
        yield Registry.DBPOOL.runQuery('''CREATE TABLE environments(
             id INTEGER PRIMARY KEY ,
             name TEXT,
             status TEXT NOT NULL DEFAULT "Live",
             description TEXT
             )''')
    @defer.inlineCallbacks
    def _generateDatabase(self):
        yield Registry.DBPOOL.runQuery('''CREATE TABLE addons(
             id INTEGER PRIMARY KEY,
             name TEXT,
             description TEXT,
             active boolean NOT NULL default true           
             )''')
        yield Registry.DBPOOL.runQuery('''CREATE TABLE environments(
             id INTEGER PRIMARY KEY,
             name TEXT,
             description TEXT,
             status TEXT NOT NULL DEFAULT "Live"
             )''')
        
        yield Registry.DBPOOL.runQuery('''CREATE TABLE nodes(
             id INTEGER PRIMARY KEY AUTOINCREMENT,
             environment_id INTEGER NOT NULL,
             type TEXT NOT NULL ,
             name TEXT,          
             description TEXT,
             recipe TEXT,
            FOREIGN KEY(environment_id) REFERENCES environments(id) 
             )''')
        
      #FOREIGN KEY(node_id) REFERENCES nodes(id)  
        yield Registry.DBPOOL.runQuery('''CREATE TABLE drivers(
             id INTEGER PRIMARY KEY AUTOINCREMENT,
             node_id INTEGER NOT NULL,
             driverType TEXT NOT NULL,
             deviceType TEXT NOT NULL ,
             deviceId TEXT,
             options BLOB  ,
             FOREIGN KEY(node_id) REFERENCES nodes(id)      
             )''')
        
        yield Registry.DBPOOL.runQuery('''CREATE TABLE tasks(
             id INTEGER PRIMARY KEY AUTOINCREMENT,
             environment_id INTEGER NOT NULL,
             name TEXT,          
             description TEXT,
             type TEXT,
             params TEXT,
             FOREIGN KEY(environment_id) REFERENCES environments(id)  
             )''')
        yield Registry.DBPOOL.runQuery('''CREATE TABLE actions(
             id INTEGER PRIMARY KEY AUTOINCREMENT,
             task_id INTEGER NOT NULL,
             actionType TEXT,          
             params TEXT,
             FOREIGN KEY(task_id) REFERENCES tasks(id)
             )''')
        yield Registry.DBPOOL.runQuery('''CREATE TABLE conditions(
             id INTEGER PRIMARY KEY AUTOINCREMENT,
             task_id INTEGER NOT NULL,
             name TEXT,          
             description TEXT,
             FOREIGN KEY(task_id) REFERENCES tasks(id)
             )''')
        
       
             
        yield Registry.DBPOOL.runQuery('''CREATE TABLE sensors(
             id INTEGER PRIMARY KEY AUTOINCREMENT,
             node_id INTEGER NOT NULL,
             captureType TEXT NOT NULL,
             captureMode TEXT NOT NULL DEFAULT "Analog",
             type TEXT NOT NULL ,
             realName TEXT NOT NULL,
             name TEXT,
             description TEXT,
             FOREIGN KEY(node_id) REFERENCES nodes(id)
             )''')
        
        yield Registry.DBPOOL.runQuery('''CREATE TABLE readings(
             id INTEGER PRIMARY KEY AUTOINCREMENT,
             node_id INTEGER NOT NULL,
             sensor_id INTEGER NOT NULL,
             data INTEGER NOT NULL,
             dateTime TEXT NOT NULL,
             FOREIGN KEY(node_id) REFERENCES nodes(id),
             FOREIGN KEY(sensor_id) REFERENCES sensors(id)
             )''')
        """this should be in the master db, but will have to do for now (only support for one environment,
        because of the limitations of twistar: one db )"""
        
        yield Registry.DBPOOL.runQuery('''CREATE TABLE updates(
             id INTEGER PRIMARY KEY AUTOINCREMENT,
             type TEXT NOT NULL,
             name TEXT NOT NULL,
             description TEXT,
             version TEXT NOT NULL,
             downloadUrl TEXT NOT NULL,
             tags TEXT NOT NULL,
             img TEXT NOT NULL,
             file TEXT NOT NULL,
             fileHash TEXT NOT NULL,
             downloaded TEXT NOT NULL,
             installed TEXT NOT NULL,
             enabled TEXT NOT NULL
             
             )''')
        
        defer.returnValue(None)
      
#        Registry.DBPOOL.runQuery('''CREATE TABLE Actors(
#            id INTEGER PRIMARY KEY AUTOINCREMENT,
#             env_id INTEGER NOT NULL,
#             node_id INTEGER NOT NULL,
#             auto_id INTEGER NOT NULL DEFAULT 1,
#             realName TEXT NOT NULL,
#             params TEXT,
#             name TEXT,
#             description TEXT,
#             FOREIGN KEY(env_id) REFERENCES Environments(id),
#             FOREIGN KEY(node_id) REFERENCES Nodes(id),
#             FOREIGN KEY(auto_id) REFERENCES Automation(id)
#             )''').addCallback(self._dbGeneratedOk) 
    