#        d=defer.Deferred()
#        d.addCallback(self.error_test)
#        d.addErrback(self.error_test_errb1)
#        d.addCallbacks(self.callbck_2,self.error_test_errb2)
#        d.addBoth(self.final_callbackErrback,request)
#        d.callback(None)
#        return NOT_DONE_YET



    def _build_resource_uri(self,resourceInstance=None,resourceName=""):
        """
        builds the current resource uri /link, based on resource name and root uri
        """
        self.rootUri=""
        item={}
        item["link"]={}
        item["link"]["rel"]=resourceName
        if resourceInstance:   
            item["link"]["href"]=self.rootUri+str(resourceInstance.id)
            item=dict(item.items() + resourceInstance._toDict().items())
        else:
            item["link"]["href"]=self.rootUri
        print("item",item)
        return item
            
    def _build_resource_list_uri(self,list,resourceName):
        """
        generates a dictionary based data structure for a set of links in json, based on a list
        and a resource name
        """
        result={}
        result[resourceName+"s List"]={}
        result[resourceName+"s List"]["link"]={}
        result[resourceName+"s List"]["link"]["href"]=self.rootUri
        result[resourceName+"s List"]["link"]["rel"]=resourceName+"s"
        result[resourceName+"s List"]["items"]=[self._build_resource_uri(item,resourceName)for item in list] 
        
        return result
    
    


def error_test(self,result):
        #raise Exception("totot")
        raise KpouerError()
        raise TestError()
        return "tutu"
    
    def error_test_errb1(self,failure):
        print("first errback",str(failure))
        return failure
    
    def error_test_errb2(self,failure):
        print("second errback",str(failure))
        return failure
    def callbck_2(self,result):
        print("second callback",str(result))
        
    def final_callbackErrback(self,result,request):
        print("final callbackerrback")
        if isinstance(result,failure.Failure):
            print("grabbed failure")
            #print(result.getErrorMessage())
            #print(result.getBriefTraceback())
            types=[KpouerError,TestError]
            v=result.check(*types)
            print("failure exception",v)
            if v==KpouerError:
                return self._build_response(result,request,501,"application/pollapli.environmentsList+json",1,"kpouer error")
            elif v==TestError:
                self._build_response(result,request,502,"application/pollapli.environmentsList+json",2,"test error")

        else:
            self._build_response(result,request,200,"application/pollapli.environmentsList+json",)

            print("no failure here")


#        d.addCallback(self._parse_query_params)
#        d.addCallbacks(callback=self.result_dict_extractor,errback=self._handle_query_error,callbackKeywords={"callback":self.environmentManager.add_environment})    
#
#        #d.addCallbacks(self.print_result,errback=self._handle_query_error)
#        d.callback(request)
        #d.callback(request)
        
            
#        def big_fail(failure):
#                print("epic fail",failure.exception)
#        try:
#            d=Deferred()
#            d.add_callback(self.dummy_test)
#            d.add_callback(self._parse_query_params)
##            d.add_callbacks(callback=self.result_dict_extractor,errback=self._handle_query_error,callbackKeywords={"callback":self.environmentManager.add_environment})    
##            d.add_callbacks(callback=self._build_resource_uri,callbackKeywords={"resourceName":"environment"},errback=self._env_add_failure)
##            d.add_callbacks(callback=self._build_valid_response,callbackKeywords={"request":request,"status":200,"contentType":"text/html"},errback=big_fail)    
#            d.start(request)
#        except Exception as inst:
#            print("error in post",inst)
#        print(d.result)
#        return d.result