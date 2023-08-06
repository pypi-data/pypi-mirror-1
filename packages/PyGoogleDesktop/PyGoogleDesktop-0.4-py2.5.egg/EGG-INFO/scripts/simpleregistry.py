"""
Simplest Windows Registry I/0
Title: Simplest Registry I/O
Submitter: Jack Trainor (other recipes)
Last Updated: 2007/08/24
Version no: 1.0
Category: System
http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/528896	
 
Description:

Most of the time I just want to either read or write one value to the registry. 
Here are two functions: ReadRegistryValue and WriteRegistryValue plus a few helpers.
"""
import win32api
import win32con

def ReadRegistryValue(hiveKey, key, name=""):
    """ Read one value from Windows registry. If 'name' is empty string, reads default value."""
    data = typeId = None
    try:
        keyHandle = win32api.RegOpenKeyEx(hiveKey, key, 0, win32con.KEY_ALL_ACCESS)
        data, typeId = win32api.RegQueryValueEx(keyHandle, name)
        win32api.RegCloseKey(keyHandle)
    except Exception, e:
        print "ReadRegistryValue failed:", hiveKey, key, name, e
    return data, typeId

def WriteRegistryValue(hiveKey, key, name, data, typeId=win32con.REG_SZ):
    """ Write one value to Windows registry. If 'name' is empty string, writes default value.
        Creates subkeys as necessary"""
    try:
        keyHandle = OpenRegistryKey(hiveKey, key)
        win32api.RegSetValueEx(keyHandle, name, 0, typeId, data)
        win32api.RegCloseKey(keyHandle)
    except Exception, e:
        print "WriteRegistryValue failed:", hiveKey, name, e

def OpenRegistryKey(hiveKey, key):
    """ Opens a keyHandle for hiveKey and key, creating subkeys as necessary """
    keyHandle = None
    try:
        curKey = ""
        keyItems = key.split('\\')
        for subKey in keyItems:
            if curKey:
                curKey = curKey + "\\" + subKey
            else:
                curKey = subKey
            keyHandle = win32api.RegCreateKey(hiveKey, curKey)
    except Exception, e:
        keyHandle = None
        print "OpenRegistryKey failed:", hiveKey, key, e
    return keyHandle

def DeleteRegistryKey(hiveKey, key):
    """ Deletes a registry key -- must be a leaf key or call fails """
    try:
        result = win32api.RegDeleteKey(hiveKey, key)
        return result
    except Exception, e:
        print "DeleteRegistryKey failed:", hiveKey, key, e
    return None

def TestRegistryWriteRead(hiveKey, key, name, data, typeId):
    WriteRegistryValue(hiveKey, key, name, data, typeId)
    outputData, outputTypeId = ReadRegistryValue(hiveKey, key, name)
    status = "OK"
    if (outputData != data or outputTypeId != typeId):
        status = "FAILED"
    print "%s -- %d %s %s -- input: %s %s  output: %s %s" % \
        (status, hiveKey, key, name, str(data), str(typeId), str(outputData), str(outputTypeId))

def Test():
    TestRegistryWriteRead(win32con.HKEY_LOCAL_MACHINE, "Software\\AAAAA", "", "this is a default value", win32con.REG_SZ)
    TestRegistryWriteRead(win32con.HKEY_LOCAL_MACHINE, "Software\\AAAAA", "Data-SZ", "this is a string", win32con.REG_SZ)
    TestRegistryWriteRead(win32con.HKEY_LOCAL_MACHINE, "Software\\AAAAA", "Data-BINARY", '\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09', win32con.REG_BINARY)
    TestRegistryWriteRead(win32con.HKEY_LOCAL_MACHINE, "Software\\AAAAA", "Data-DWORD", 0x01234567, win32con.REG_DWORD)
    DeleteRegistryKey(win32con.HKEY_LOCAL_MACHINE, "Software\\AAAAA")
    
if __name__ == "__main__":
    Test()
