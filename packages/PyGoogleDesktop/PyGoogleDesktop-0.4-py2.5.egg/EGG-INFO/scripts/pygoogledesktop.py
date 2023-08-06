"""
@summary: A simple python interface into the google desktop engine that will allow
           any python program to use the search engine.


@author: Jack G. Atkinson Jr.
@organization: Doxa Logos Technologies, Inc.
@copyright: (c) 2008, Doxa Logos Technologies, Inc. 
@license: BSD-Style (see license.txt)
@version: 0.2
@requires: Python 2.4 and the win32all extensions for Python 2.4 on Windows.
Will not work unless Google Desktop Search 1.0 or later is installed.

@history:  0.4 - changed the way the debug.log is handled
"""
#TODO: do a cross platform check for conditional importing (i.e. no win32,pythoncom,pywintypes import for Mac platform)
import sys
import win32com.client
import pythoncom
import pywintypes


class PyGDS(object):
    """
    PyGDS is the main interface into the Google Desktop Search Engine.  It's designed to simplify interactions
    with GDS, instead of laying out the complete bare interface to GDS.

    """
    def __init__(self):
        self.debugInit = False
        return

    def EnableDebug(self):
        if(self.debugInit):
            self.logging.disable(logging.NOTSET)
        else:
            #temporary
            import logging
            self.logging.basicConfig(level=logging.DEBUG,
                            format='%(asctime)s %(levelname)s %(message)s',
                            filename='debug.log',
                            filemode='w')
            self.debugInit = True
        return

    def DisableDebug(self):
        if(self.debugInit):
            self.logging.disable(logging.CRITICAL)
        return

    def RegisterAppQueryAPI(self, guid, desc, readOnly):
        """
        Register your application with GoogleDestkopSearch engine.
        This is only required if you want to use the "DoQuery"
        function of this interface. Don't need to register if you
        use DoQueryHTTP.
        
        @param guid: guidgen.exe param of your application
        @param desc: a dictionary of the description
                     'title' = the name of your app
                     'description' = desription of the app
                     'icon' = icon of your app   
        @param readOnly:   Are going to be doing read only queries? True = yes, False = no
        @return: the cookie from the query registration
        """
        cookie = None
        #Go ahead and start registration
        try:
            registrar = win32com.client.Dispatch('GoogleDesktop.Registrar')
        except pythoncom.ole_error:
            print ('ERROR: You need to install Google Desktop Search to be able to '
                    'use it.')
            if(self.debugInit):
                logging.error("Failed to get Registrar, exit")
            sys.exit(2)

        #register the component
        registrar.StartComponentRegistration(guid,['Title', desc['title'], 'Description',desc['description'],
                                                 'Icon',desc['icon']])

        queryReg = registrar.GetRegistrationInterface("GoogleDesktop.QueryRegistration")
        cookie =  queryReg.RegisterPlugin(guid,readOnly)
        if(self.debugInit):
            logging.debug("Query plugin registered!")
        #TODO:  your app needs to add cookie encryption and adding to registry


        try: 
            registrar.FinishComponentRegistration() 
            if(self.debugInit):
                logging.debug("App Registered!")
        except pythoncom.com_error:
            if(self.debugInit):
                logging.debug("Already Registered")
            pass
        except pythoncom.ole_error:
            registrar.UnregisterComponent(guid)
            if(self.debugInit):
                logging.debug("Failed to finish registration")
            return None

        return cookie


    def UnRegisterApp(self,guid):
        """
        UnRegister your application with GoogleDestkopSearch engine.
        
        @param guid: guidgen.exe param of your application
        @return: true if it unregistered
        """
        try:
            registrar = win32com.client.Dispatch('GoogleDesktop.Registrar')
        except pythoncom.ole_error:
            print ('ERROR: You need to install Google Desktop Search to be able to '
                    'use it.')
            if(self.debugInit):
                logging.error("Failed to get Registrar, exit")
            sys.exit(2)

        registrar.UnregisterComponent(guid)
        if(self.debugInit):
            logging.debug("App unregistered!")
        return True


    def DoQuery(self,cookie,searchStr,category=None,relevance=False):
        """
        Perform a simple query using the cookie passed into it.
        This cookie must be unencrypted at this point for the GoogleDesktop to know
        what it is.
        
        @param cookie: the cookie returned during registration of your app with GDS. 
        @param searchStr: the string used to search on
        @param category: filter the results based on a category. Valid values are
                           Email,Web,Im,File,Contact,Calendar,Task,Note, or Journal
        @param relevance: - sort by relevance (True) or recency (False)
        @return: a list of tuple results (uri,content) - None if something went wrong
        @note: if the content is not retrievable, None will be in it's place.  Check
               to make sure the data is valid.
        """
        if(self.debugInit):
            logging.debug("begin DoQuery")
        #retrieve query API from GDS
        try:
            queryApi = win32com.client.Dispatch('GoogleDesktop.QueryAPI')
        except pythoncom.ole_error:
            print ('ERROR: You need to install Google Desktop Search to be able to '
                    'use it.')
            if(self.debugInit):
                logging.error("Failed to get QueryAPI,exit")
            sys.exit(2)

        #perform Query
        try:
            if(category != None):
                results = queryApi.Query(cookie,searchStr,category)
            else:
                results = queryApi.Query(cookie,searchStr)

        except pythoncom.ole_error,e:
            if(self.debugInit):
                logging.error("OLE_ERROR: Couldn't perform Query")
            if len(e.args) > 0:
                for x in e.args:
                    logging.error(x)
            return None
        except UnicodeEncodeError:
            if(self.debugInit):
                logging.error("UnicodeEncodeError on Query")
            pass
        #store results into a list of tuples
        try:
            item = results.Next()
        except UnicodeEncodeError:
            if(self.debugInit):
                logging.error("UnicodeEncodeError on Query")
            pass
        queryList = []
        count = 0
        while(item != None):
            schema = item.schema
            if(self.debugInit):
                logging.debug(schema)
            uri = item.GetProperty("uri")
            if(self.debugInit):
                logging.debug("URI " + uri)
            #check which schemas have printable content
            if(schema.find("TextFile") != -1 or schema.find("Email") != -1 or 
                    schema.find("WebPage") != -1):
                try:
                    content = item.GetProperty("content")
                except pythoncom.com_error:
                    #okay, so this one could not print for some reason
                    queryList.append((uri,None))
                else:
                    #logging.debug("CONTENT " + content)
                    queryList.append((uri,content))
            else:
                queryList.append((uri,None))
                
            count += 1
            try:
                item = results.Next()
            except UnicodeEncodeError:
                logging.error("UnicodeEncodeError on next result")
                pass
            except pythoncom.ole_error:
                logging.error("OLE_ERROR: next result")
                pass

        if(self.debugInit):
            logging.debug('The count is ' + str(count))
        return queryList

    def DoQueryHTTP(self,searchStr,numResults=10, category=None,relevance=False,rawXMLReturn=False,extension=None):
        """
        DoQueryHTTP uses the GDS webserver interface and returns results
        in XML.  However, this function will parse the XML into a more
        user friendly formatted list for looking at the results.  In the 
        future this will become a cross platform function.

        @param searchStr: the text you want to search.  Note, if you
                          specify a string with spaces in between words
                          this will be interpreted as multiple words
                          to search.

        @param numResults: The number of results you want returned from this query.
                           Default = 10, if 0 specified, then return all!
        @param category: filter the results based on a category. Valid values are
                           email,web,im,file,contact,calendar,task,note, or journal
        @param relevance:  sort by relevance (True) or recency (False) (Not implemented)
        @param rawXMLReturn: return the results in raw XML format (yes = True, no = False)
        @param extension: Only used for category = file.  Specify the file extensions to be searched,
                          separate extension by comma (cpp,hpp,txt,html)
        @return: This will return either raw xml for you to parse or an tuple with number of times it found 
                 your search term and a python list with the location of the resources matching the 
                 search term

        """
        #TODO: conditional import for windows32 vs Mac
        import simpleregistry
        import win32con as wc

        #grab the search url
        try:
            GDSurl,typeId = simpleregistry.ReadRegistryValue(wc.HKEY_CURRENT_USER,"Software\\Google\\Google Desktop\\API", "search_url")
        except:
            print ('ERROR: You need to install Google Desktop Search to be able to '
                    'use it.')
            if(self.debugInit):
                logging.error("Failed to find Google Desktop Search URL")
            sys.exit(2)

        if(self.debugInit):
            logging.debug(GDSurl)
        #construct the query
        newSearch = searchStr.replace(" ","+").replace("\"","\%22")
        if(self.debugInit):
            logging.debug(newSearch)
        #search until you get them all
        numResults = int(numResults)
        if(numResults == 0):
            numberOfResults = 1
        else:
            numberOfResults = numResults
        url = GDSurl + newSearch + "&num="+str(numberOfResults)+"&format=xml"
        #send the http request
        results = self.SendHTTPRequest(url)
        #check no results
        checkResults = results.split("\"")
        if(int(checkResults[7]) == 0):
            if(self.debugInit):
                logging.debug("No results found!")
            if(rawXMLReturn):
                return results
            else:
                return 0,[]
#        logging.debug(results)
        count, parsedResults =  self.ParseHTTPResults(results,category,extension)
        if(numResults != 0):
            if(rawXMLReturn):
                return results
            else:
                return count, parsedResults
        else:
            if(self.debugInit):
                logging.debug(count)
            #build string one more time
            url = GDSurl + newSearch + "&num=" + str(count) + "&format=xml"
            #send request again
            results = self.SendHTTPRequest(url)
            #handle parsing
            if(rawXMLReturn):
                return results
            else:
                return self.ParseHTTPResults(results,category,extension)


    
    def CheckSuffix(self,testStr,suffix):
        """
        Checks the suffix since before Python 2.5 doesn't have the
        tuple check for string method "endswith".

        @param testStr: you're test string 
        @param suffix: the file extension you're testing to see is at the end of the string
        @return: True if it is in there, False if not
        """

        for x in suffix.split(','):
            if(testStr.endswith(x)):
                return True

        return False

    def SendHTTPRequest(self,url):
        """
        Send the url to Google Desktop Search Engine

        @param url: the uniform resource locator
        @return: raw xml results
        """
        import urllib
        data = urllib.urlopen(url)
        results = data.read()
        if(self.debugInit):
            logging.debug(results)
        return results

    def ParseHTTPResults(self,results,category,extension):
        """
        Parse the xml results into a list

        @param results: the xml results from the HTTP Query
        @param category: what kind of item were you wanting to retrieve
        @param extension: what file extension are you looking for if the categor is 'file'
        @return: number of times the search words were found, list of the parsed results
        """
        import xml2obj
        queryList = []
        resultsObj = xml2obj.xml2obj(results)
        if(self.debugInit):
            logging.debug(resultsObj.count)
        for data in resultsObj.result:
            try:
                cat = str(data['category'])
                tit = str(data['title'])
                uri = str(data['url']).replace("\\\\","\\")
                if((category == None or cat == category) and extension == None):
                    queryList.append((cat,tit,uri))
                    if(self.debugInit):
                        logging.debug((cat,tit,uri))
                elif(category == 'file' and cat == category and self.CheckSuffix(uri,extension)):
                    queryList.append((cat,tit,uri))
                    if(self.debugInit):
                        logging.debug((cat,tit,uri))

            except UnicodeEncodeError:
                if(self.debugInit):
                    logging.error("UnicodeEncodeError on next result")
                pass

        return resultsObj.count,queryList
