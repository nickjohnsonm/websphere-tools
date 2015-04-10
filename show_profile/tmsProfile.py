# Copyright 2012 - The Middleware Shop
# Profile script
# ===============================================
# Tested with WAS 8.0 and WAS 7.0 in CentOS 6.2
# ===============================================
print "tmsProfile.py: Importing necessary packages..."
import java.lang as lang
from java.io import ByteArrayInputStream
from org.xml.sax import InputSource
from javax.xml.parsers import DocumentBuilderFactory
from javax.xml.xpath import XPath, XPathFactory, XPathExpression, XPathConstants
from org.w3c.dom import Document
from org.w3c.dom import Node
from org.w3c.dom import NodeList as XPathNodeList
import os
import glob
print "tmsProfile.py: Importing necessary packages...Done"
# Initialize useful variables
print "tmsProfile.py: Initializing global variables..."
WAS_ROOT = lang.System.getProperty("was.install.root")
print "tmsProfile.py: Initializing global variables...Done"
###############################################################################
# Class: XPath Util
#        Can be used to obtain XML nodes from an XML doc that satisfies an Xpath
###############################################################################
print "tmsProfile.py: Loading XpathUtil..."
class XpathUtil:
    #Instance Variables
    #None
    def __init__(self):
        pass	
    def findXpathNodes(self, xmlAsText, xpathExpr):
        xmlText = InputSource(ByteArrayInputStream(lang.String(xmlAsText).getBytes()))
        docBuilderFactory = DocumentBuilderFactory.newInstance()
        docBuilderFactory.setValidating(0)
        docBuilderFactory.setNamespaceAware(0)
        docBuilder = docBuilderFactory.newDocumentBuilder()
        doc = docBuilder.parse(xmlText)
        xpathFactory = XPathFactory.newInstance()
        xPath = xpathFactory.newXPath()
        expr = xPath.compile(xpathExpr);

        nodeList = expr.evaluate(doc, XPathConstants.NODESET)
        nodeCount = nodeList.getLength()
        count = 0
        xpathNodes = []
        while count < nodeCount:
            xpathNodes.append(nodeList.item(count))
            count = count + 1
        return xpathNodes
print "tmsProfile.py: Loading XpathUtil...Done"
###############################################################################
# Class: Port
#        Just a data transfer object that holds port details
###############################################################################
print "tmsProfile.py: Loading Port..."
class Port:
    #Instance Variables
    __portNumber     = None
    __portName       = None
    __serverName     = None
    __profileName    = None
    __cellName       = None
    __nodeName       = None
    def __init__(self, portNumber, portName, serverName, profileName, cellName, nodeName):
        self.__portNumber = portNumber
        self.__portName = portName
        self.__serverName = serverName
        self.__profileName = profileName
        self.__cellName = cellName
        self.__nodeName = nodeName

    def getPortNumber(self):
        return self.__portNumber;
    def getPortName(self):
        return self.__portName;
    def getServerName(self):
        return self.__serverName;
    def getProfileName(self):
        return self.__profileName;
    def getCellName(self):
        return self.__cellName;
    def getNodeName(self):
        return self.__nodeName;
print "tmsProfile.py: Loading Port...Done"
###############################################################################
# Class: Profile
#        Profile object knows WAS profile specifics
#        Profile objects can be obtained through ProfileRegistry
###############################################################################
print "tmsProfile.py: Loading Profile..."
class Profile:
    #Instance Variables
    __profilePath    = None
    __profileName    = None
    #managed profiles are managed by a deployment manager
    __managed        = None
    def __init__(self, profilePath, profileName, managed):
        self.__profilePath = profilePath
        self.__profileName = profileName
        self.__managed = managed
    def isManaged(self):
        return self.__managed
    def getProfileName(self):
        return self.__profileName
    def getWasPorts(self):
        # Gives an array of paths that points to serverindex.xml files
        siPaths = glob.glob(os.path.join(self.__profilePath,'config','cells','*','nodes','*','serverindex.xml'))
        ports = []
        for siPath in siPaths:
            #split the path into a folder list
            foldersInPath = siPath.split(os.sep)
            #The node name appears just before serverindex.xml in the list		
            #/opt/IBM/WebSphere/AppServer/profiles/appsrv09/config/cells/localhostNode03Cell/nodes/node09/serverindex.xml
            nodeName = foldersInPath[len(foldersInPath) - 2]
            cellName = foldersInPath[len(foldersInPath) - 4]
            siFile = open(siPath)
            siXmlText = siFile.read()
            x = XpathUtil()
            serverNodes = x.findXpathNodes(siXmlText, "//ServerIndex/serverEntries/@serverName")
            for serverNode in serverNodes:
                serverName = serverNode.getNodeValue()
                self.__profilePorts(siXmlText, serverName, nodeName, cellName, ports)
        return ports
    #This is a private method that creates port objects by parsing serverindex.xml file
    def __profilePorts(self, serverIndexStr, serverName, nodeName, cellName, ports):
        x = XpathUtil()
        xp = "//ServerIndex/serverEntries[@serverName='"+serverName+"']/specialEndpoints/@id"
        portNodeIds = x.findXpathNodes(serverIndexStr,xp)
        for pnID in portNodeIds:
            idStr = pnID.getNodeValue()
            nxp = "//ServerIndex/serverEntries[@serverName='"+serverName+"']/specialEndpoints[@id='"+idStr+"']/@endPointName"
            pxp = "//ServerIndex/serverEntries[@serverName='"+serverName+"']/specialEndpoints[@id='"+idStr+"']/endPoint/@port"
            pName = x.findXpathNodes(serverIndexStr,nxp)
            pNum = x.findXpathNodes(serverIndexStr,pxp)
            p = Port(pNum[0].getNodeValue(),pName[0].getNodeValue(),serverName,self.__profileName,cellName,nodeName)
            ports.append(p)
print "tmsProfile.py: Loading Profile...Done"
###############################################################################
# Class: ProfileRegistry
#        Provides a list of profile objects
###############################################################################
print "tmsProfile.py: Loading ProfileRegistry..."
class ProfileRegistry:
    #Instance Variables
	#None
    def __init__(self):
        pass
    def getProfileList(self):
        # Open profile registry and obtain the list of profiles
        profileRegistryFile = open(WAS_ROOT+"/properties/profileRegistry.xml")
        profileRegistryStr = profileRegistryFile.read()
        #print profileRegistryStr
        x = XpathUtil()
        profileNameNodes = x.findXpathNodes(profileRegistryStr, "//profiles/profile/@name")
        profiles = []
        for profileNameNode in profileNameNodes:
            profileName = profileNameNode.getNodeValue()
            profilePathNode = x.findXpathNodes(profileRegistryStr, "//profiles/profile[@name='"+profileName+"']/@path")
            profileTmplNode = x.findXpathNodes(profileRegistryStr, "//profiles/profile[@name='"+profileName+"']/@template")
            profileTempl = profileTmplNode[0].getNodeValue();
            profilePath = profilePathNode[0].getNodeValue()
            profile = Profile(profilePath, profileName, profileTempl.endswith("managed"))
            profiles.append(profile)
        return profiles			
print "tmsProfile.py: Loading ProfileRegistry...Done"
###############################################################################
# getWasPorts() prints all the ports in use in a given WAS 8.0 Installation
#   First it obtains a list of profiles from profileRegistry.xml
#       Iterate through the profiles
#       For every profile check if its template is "managed" or not (Ignore managed ones)
#           Profile object obtains ports numbers by reading serverindex.xml files 
###############################################################################
print "tmsProfile.py: Loading getWasPorts function..."
def getWasPorts():
    profileList = ProfileRegistry().getProfileList()
    ports = []
    for profile in profileList:
        # If a profile has a "managed" template, ignore
        #   as otherwise ports will be listed twice, once for dmgr and once for the managed node.
        if not profile.isManaged():
            ports.extend(profile.getWasPorts())
    return ports
print "tmsProfile.py: Loading getWasPorts function...Done"
def printWasPorts():
    ports = getWasPorts()
    print "%-15s %-15s %-15s %10s  %-30s" % ("Profile", "Node", "Server", "Port","Name")
    print "%-15s %-15s %-15s %10s  %-30s" % ("=======", "====", "======", "====","====")
    for p in ports:
	    print "%-15s %-15s %-15s %10s  %-30s" % (p.getProfileName(), p.getNodeName(), p.getServerName(), p.getPortNumber(),p.getPortName())



