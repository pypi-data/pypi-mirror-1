import os
import pickle

from datetime import datetime
        
class PickleComments(object):
    # TODO: locking
    def __init__(self, database):
        self.database = database
        if not os.path.exists(database):
            f = file(database, 'w')
            pickle.dump({}, f)
            f.close()

    def comment(self, uri, **kw):
        f = file(self.database)
        comments = pickle.load(f)
        f.close()
        comments.setdefault(uri, []).append(kw)
        f = file(self.database, 'w')
        comments = pickle.dump(comments, f)
        f.close()

    def comments(self, uri):
        f = file(self.database)
        comments = pickle.load(f)
        f.close()
        return comments.get(uri, [])

    
try:
    import couchdb

    class CouchComments(object):
        def __init__(self, db):
            self.couch = couchdb.Server()
            if db not in self.couch:
                self.db = self.couch.create(db)
            else:
                self.db = self.couch[db]

        def comment(self, uri, **kw):
            if uri in self.db:
                comments = self.db[uri]['comments']
                comments.append(kw)
                self.db[uri] = { 'comments': comments }
            else:
                self.db[uri] = { 'comments': [ kw ] }

        def comments(self, uri):
            if uri in self.db:
                doc = self.db[uri]
                return doc ['comments']
            return []

except ImportError:
    pass
