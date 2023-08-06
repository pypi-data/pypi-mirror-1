"""The application's Globals object"""

import os
from lxml.builder import ElementMaker
from lxml import etree

class Globals(object):

    """Globals acts as a container for objects available throughout the
    life of the application

    """

    relaxNGSchemaNamespace="http://relaxng.org/ns/structure/1.0"
    eRelaxNG = ElementMaker(namespace=relaxNGSchemaNamespace,nsmap={None:relaxNGSchemaNamespace})

    darcsRelaxNGDoc = eRelaxNG("grammar",
        eRelaxNG("start",
            eRelaxNG("element",
                eRelaxNG("interleave",
                    eRelaxNG("element",
                        eRelaxNG("ref","",name="globalContent"),
                    name="global"),
                    eRelaxNG("optional",
                        eRelaxNG("element",
                            eRelaxNG("ref","",name="defaultsContent"),
                        name="defaults")
                    ),
                    eRelaxNG("oneOrMore",
                        eRelaxNG("element",
                            eRelaxNG("ref","",name="repositoryContent"),
                        name="repository")
                    ),
                ),
            name="settings")
        ),
        eRelaxNG("define",
            eRelaxNG("optional",
                eRelaxNG("attribute","",name="description"),
            ),
            eRelaxNG("text"),
        name="stringContent"),
        eRelaxNG("define",
            eRelaxNG("optional",
                eRelaxNG("attribute","",name="description"),
            ),
            eRelaxNG("data","",type="integer"),
        name="integerContent"),
        eRelaxNG("define",
            eRelaxNG("optional",
                eRelaxNG("attribute","",name="description"),
            ),
            eRelaxNG("data","",type="double"),
        name="floatContent"),
        eRelaxNG("define",
            eRelaxNG("optional",
                eRelaxNG("attribute","",name="description"),
            ),
            eRelaxNG("choice",
                eRelaxNG("value","yes"),
                eRelaxNG("value","true"),
                eRelaxNG("value","no"),
                eRelaxNG("value","false"),
            ),
        name="booleanContent"),
        eRelaxNG("define",
            eRelaxNG("optional",
                eRelaxNG("attribute","",name="description"),
            ),
            eRelaxNG("choice",
                eRelaxNG("value","0",type="integer"),
                eRelaxNG("value","1",type="integer"),
                eRelaxNG("value","2",type="integer"),
                eRelaxNG("value","3",type="integer"),
                eRelaxNG("value","4",type="integer"),
                eRelaxNG("value","5",type="integer"),
            ),
        name="keyringTrustContent"),
        eRelaxNG("define",
            eRelaxNG("interleave",
                eRelaxNG("optional",
                    eRelaxNG("element",
                        eRelaxNG("ref","",name="stringContent"),
                    name="darcs"),
                ),
                eRelaxNG("optional",
                    eRelaxNG("element",
                        eRelaxNG("ref","",name="stringContent"),
                    name="darcs-options"),
                ),
                eRelaxNG("element",
                    eRelaxNG("ref","",name="stringContent"),
                name="keyring-location"),
                eRelaxNG("element",
                    eRelaxNG("ref","",name="stringContent"),
                name="quarantine-location"),
            ),
        name="globalContent"),
        eRelaxNG("define",
            eRelaxNG("interleave",
                eRelaxNG("optional",
                    eRelaxNG("element",
                        eRelaxNG("ref","",name="booleanContent"),
                    name="allow-read"),
                ),
                eRelaxNG("optional",
                    eRelaxNG("element",
                        eRelaxNG("ref","",name="booleanContent"),
                    name="allow-write"),
                ),
                eRelaxNG("optional",
                    eRelaxNG("element",
                        eRelaxNG("ref","",name="stringContent"),
                    name="verify-read"),
                ),
                eRelaxNG("optional",
                    eRelaxNG("element",
                        eRelaxNG("ref","",name="stringContent"),
                    name="verify-write"),
                ),
                eRelaxNG("optional",
                    eRelaxNG("element",
                        eRelaxNG("ref","",name="integerContent"),
                    name="quarantine-max-patches"),
                ),
                eRelaxNG("optional",
                    eRelaxNG("element",
                        eRelaxNG("ref","",name="floatContent"),
                    name="quarantine-max-size"),
                ),
                eRelaxNG("optional",
                    eRelaxNG("element",
                        eRelaxNG("ref","",name="floatContent"),
                    name="patch-max-size"),
                ),
                eRelaxNG("optional",
                    eRelaxNG("element",
                        eRelaxNG("ref","",name="keyringTrustContent"),
                    name="keyring-min-trust"),
                ),
            ),
        name="defaultsContent"),
        eRelaxNG("define",
            eRelaxNG("interleave",
                eRelaxNG("element",
                    eRelaxNG("ref","",name="stringContent"),
                name="name"),
                eRelaxNG("element",
                    eRelaxNG("ref","",name="stringContent"),
                name="location"),
                eRelaxNG("optional",
                    eRelaxNG("element",
                        eRelaxNG("ref","",name="booleanContent"),
                    name="allow-read"),
                ),
                eRelaxNG("optional",
                    eRelaxNG("element",
                        eRelaxNG("ref","",name="booleanContent"),
                    name="allow-write"),
                ),
                eRelaxNG("optional",
                    eRelaxNG("element",
                        eRelaxNG("ref","",name="stringContent"),
                    name="verify-read"),
                ),
                eRelaxNG("optional",
                    eRelaxNG("element",
                        eRelaxNG("ref","",name="stringContent"),
                    name="verify-write"),
                ),
                eRelaxNG("optional",
                    eRelaxNG("element",
                        eRelaxNG("ref","",name="integerContent"),
                    name="quarantine-max-patches"),
                ),
                eRelaxNG("optional",
                    eRelaxNG("element",
                        eRelaxNG("ref","",name="floatContent"),
                    name="quarantine-max-size"),
                ),
                eRelaxNG("optional",
                    eRelaxNG("element",
                        eRelaxNG("ref","",name="floatContent"),
                    name="patch-max-size"),
                ),
                eRelaxNG("optional",
                    eRelaxNG("element",
                        eRelaxNG("ref","",name="keyringTrustContent"),
                    name="keyring-min-trust"),
                ),
            ),
        name="repositoryContent"),
    ns="darcs-server-config",datatypeLibrary="http://www.w3.org/2001/XMLSchema-datatypes")
    darcsRelaxNG = etree.RelaxNG(darcsRelaxNGDoc)

    defaultKeyring = "global.keyring"

    defaultGlobalSettings = \
        { "darcs": "darcs"
        , "darcs-options": ""
        }
 
    defaultRepositorySettings = \
        { "allow-read": True
        , "allow-write": False
        , "verify-read": False
        , "verify-write": defaultKeyring
        , "quarantine-max-patches": 25
        , "quarantine-max-size": 15
        , "patch-max-size": 5
        , "keyring-min-trust": 3
        }

    defaultValues = \
        { "booleanContent": ["allow-read","allow-write"]
        , "yesDefaultsToPrevious": ["verify-read","verify-write"]
        , "nonEmpty": ["name"]
        , "locationIsDirectory": ["keyring-location","quarantine-location","location"]
        , "number": ["quarantine-max-patches","quarantine-max-size","patch-max-size","keyring-min-trust"]
        }

    class Error(Exception):
        """Base class for exception in this module"""
        pass

    class InputError(Error):
        """Exception raised for error in the input.

        pretty prints the error message
        """
        def __str__(self):
            if len(self.args) == 1:
                return str(self.args[0])
            else:
                return " :: ".join(map(str,self.args))
        
       
    def __init__(self,path):
        """One instance of Globals is created during application
        initialization and is available during requests via the
        'app_globals' variable

        """

        """ given an xml configuration:
            validates it
            runs a sanity check
            populates the respective dicts with values,
                defaulting to built-in settings if None (empty)
        """
        # create the globalSettings dict and the repositories dict
        self.globalSettings = self.defaultGlobalSettings.copy()
        self.repositories={}
        # read in the user's config file and validate it
        darcsConfigDoc = etree.parse(path)
        self.darcsRelaxNG.assertValid(darcsConfigDoc)
        # populate the globalSettings dict with values. None (empty) values are defaulted
        for element in darcsConfigDoc.xpath("/d:settings/d:global",namespaces={"d":"darcs-server-config"})[0]:
            oldKey = element.tag.replace('{darcs-server-config}','').strip()
            oldValue = (lambda x: x and x.strip())(element.text)
            (key,value) = self.__filter__(oldKey,oldValue)
            if value is not None:
                self.globalSettings[key] = value
        # populate the repositories dict with values. First take values from default settings
        # then take values from repository settings
        for individualRepo in darcsConfigDoc.xpath("/d:settings/d:repository",namespaces={"d":"darcs-server-config"}):
            # create the repository dict from the name
            name = individualRepo.xpath("d:name",namespaces={"d":"darcs-server-config"})[0].text.strip()
            self.repositories[name]=self.defaultRepositorySettings.copy()
            # populate the repository dict with default values, if it exists
            for defaultRepo in (lambda x: x[0] if x else [])(darcsConfigDoc.xpath("/d:settings/d:defaults",namespaces={"d":"darcs-server-config"})):
                oldKey = defaultRepo.tag.replace('{darcs-server-config}','').strip()
                oldValue = (lambda x: x and x.strip())(defaultRepo.text)
                (key,value) = self.__filter__(oldKey,oldValue,name)
                if value is not None:
                    self.repositories[name][key] = value
            # populate the repository dict with per-repository values, excluding the name element
            for element in individualRepo:
                oldKey = element.tag.replace('{darcs-server-config}','').strip()
                oldValue = (lambda x: x and x.strip())(element.text)
                (key,value) = self.__filter__(oldKey,oldValue,name)
                if value is not None and str(key).lower() != "name":
                    self.repositories[name][key] = value
            # experimental: set reference to the repository dict as a data attribute
            # Might not work with weird names
            setattr(self,name,self.repositories[name])

    def __filter__(self,key,value,repository=None):
        """ check user input, for example:
                validate paths, check for empty values
            A return value of None is intended to indicate no change
        """
        if key in self.defaultValues["booleanContent"]:
            if value is not None:
                if value.lower() in ["yes","true"]:
                    value = True
                elif value.lower() in ["no","false"]:
                    value = False
                else:
                    raise self.InputError(value,"input was not of ['yes','true','no','false']")
        if key in self.defaultValues["yesDefaultsToPrevious"]:
            if value is not None:
                if value.lower() in ["no","false"]:
                    value = False
                elif value.lower() in ["yes","true"]:
                    if self.repositories.get(repository):
                        if str(self.repositories.get(repository).get(key)).lower() in ["no","false"]:
                            value = self.defaultKeyring
                        else:
                            value = None
                # else value stays unmodified
        if key in self.defaultValues["nonEmpty"]:
            if value is None:
                raise self.InputError("","input cannot be empty")
        if key in self.defaultValues["locationIsDirectory"]:
            if value is None or not os.path.exists(value) or not os.path.isdir(value) or os.path.islink(value):
                raise self.InputError, (value,"path does not refer to an existing directory")
        if key in self.defaultValues["number"]:
            if value is not None:
                try:
                    value = int(value)
                except ValueError:
                    value = float(value)
        return (key,value)

    def iterRepository(self):
        """generator returning repositories as attributes of self"""
        for name in self.repositories:
            yield getattr(self,name)

    # now for some convenience methods

    def is_repository(self,value):
        """True if value is a repository, False elsewise"""
        if value in self.repositories:
            return True
        else:
            return False

    def get_repository(self,value):
        """returns a dict of the repository settings (if it exists). Else returns None"""
        if self.is_repository(value):
            return self.repositories[value]
        else:
            return None

    def get_globalSettings(self):
        """returns a dict of the global settings"""
        return self.globalSettings

    def __getitem__(self,value):
        """ use instance[string] to return repository dicts based on name
        instance["global"] returns the global settings dict

        equivalent to type(x).__getitem__(x,i)

        note that item assignment/deletion (__{set,del}item__) is not supported
        """
        if self.is_repository(value):
            return self.get_repository(value)
        elif value == "global":
            return self.get_globalSettings()
        else:
            return None

    def readString(self,value):
        """ return a string ("Yes","No","Verify") representing the
            calculated read permission of the repository
        """
        if self.is_repository(value):
            if self.repositories[value]['allow-read']:
                if self.repositories[value]['verify-read']:
                    return "Verify"
                else:
                    return "Yes"
            else:
                return "No"
        else:
            return None

    def writeString(self,value):
        """ return a string ("Yes","No","Verify") representing the
            calculated write permission of the repository
        """
        if self.is_repository(value):
            if self.repositories[value]['allow-write']:
                if self.repositories[value]['verify-write']:
                    return "Verify"
                else:
                    return "Yes"
            else:
                return "No"
        else:
            return None
