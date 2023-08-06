import os
import config
import logging
import cPickle as pickle

logger = logging.getLogger("Chameleon")

class TemplateCache(object):
    def __init__(self, filename, version):
        self.filename = filename
        self.registry = {}
        self.version = version
        self.load()
        
    def __getitem__(self, key):
        return self.registry[key]

    def __setitem__(self, key, template):
        self.registry[key] = template
        self.save()

    def __len__(self):
        return len(self.registry)
    
    def get(self, key, default=None):
        return self.registry.get(key, default)
    
    @property
    def module_filename(self):
        return self.filename + os.extsep + config.CACHE_EXTENSION
    
    def load(self):
        try:
            module_filename = self.module_filename
            f = open(module_filename, 'rb')
        except IOError:
            return

        try:
            try:
                try:
                    version, registry = pickle.load(f)
                except EOFError:
                    pass
                
                if version != self.version:
                    raise ValueError("Version mismatch: %s != %s" % (
                        version, self.version))

                self.registry.update(registry)
            except ValueError, e:
                logger.warn(
                    "Error loading cache for %s (%s)." % (self.filename, str(e)))
        finally:
            f.close()
        
    def save(self):
        try:
            f = open(self.module_filename, 'wb')
        except IOError:
            return

        try:
            data = self.version, self.registry
            pickle.dump(data, f, protocol=2)
        finally:
            f.close()

    def clear(self):
        self.registry.clear()
                
    def purge(self):
        self.clear()
        self.save()
