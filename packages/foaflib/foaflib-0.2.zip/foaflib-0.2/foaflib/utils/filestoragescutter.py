from hashlib import sha1
from foaflib.utils.basicscutter import BasicScutter

class FileStorageScutter(BasicScutter):

    def __init__(self, directory, seed_uris=None): 
        BasicScutter.__init__(self, seed_uris)
        self.directory = directory

    def handle_person(self, foafperson):
        filename = self.directory + "/" + sha1((foafperson.name or "noname") + (foafperson.homepage or "nohomepage")).hexdigest()
        foafperson.save_as_xml_file(filename)
        return foafperson
