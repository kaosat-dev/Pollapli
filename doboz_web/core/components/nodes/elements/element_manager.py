    class NodeElementManager(object):
        pass
    
        """
        ####################################################################################
        The following functions are typically hardware manager/hardware nodes and sensors related, pass through methods for the most part
        """
        def add_element(self):
            pass
        def add_actor(self,envId,type,port):
            pass
        
        def remove_actor(self,envId):
            pass
        
        def add_sensor(self,id,node,params):
            """
            Add a sensor to an environment 
            Params:
            EnvName: the name of the environment
            Title: title of the sensor
            """
            self.environments[id].add_sensor(node,params)
           
        def remove_sensor(self,id,sensorId):
            """
            Remove a sensor from an environment 
            Params:
            EnvName: the name of the environment
            sensorId: id of the sensor to remove
            """
            self.environments[id]   
        
        def add_sensorType(self,envName,title, description):
            """
            Add a sensor type to an environment 
            Params:
            EnvName: the name of the environment
            Title: title of the sensorType
            Description: short description of the sensor type
            """
            self.environments[envName].add_sensorType(title, description)
            
        def remove_sensorType(self,envName,sensorTypeId):
            """
            Remove a sensor type from an environment 
            Params:
            EnvName: the name of the environment
            sensorTypeId: id of the sensor type to remove
            """
            self.environments[envName].remove_sensorType(sensorTypeId)
            
        def get_sensorData(self,criteria,startDate,endDate):
            """
            returns the data from a specific sensor in a specific node, in a specific environment
            collected between the two specified dates
            envName, nodeId , sensorId can be lists
            pass it a list of dictionaries
            as such {'envName':envName,'nodeId':nodeId,'sensorId':sensorId,'startDate':startDate,'endDate':endDate}
            {envName:{nodeId:(sensorId,sensorId2,...),nodeId2:(sensorId,sensorId2},envName2:}
            """
            for elem in criteria:
               self.environments[elem['envName']].get_sensorData(elem['nodeId'],elem['sensorId'],starDate,endDate)
    
        
        