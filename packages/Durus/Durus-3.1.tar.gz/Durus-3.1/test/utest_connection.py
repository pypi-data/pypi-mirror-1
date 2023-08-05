"""
$URL: svn+ssh://svn.mems-exchange.org/repos/trunk/durus/test/utest_connection.py $
$Id: utest_connection.py 27272 2005-09-01 19:41:28Z dbinger $
"""
from durus import run_durus
from durus.client_storage import ClientStorage
from durus.connection import Connection, touch_every_reference
from durus.error import ConflictError
from durus.file_storage import TempFileStorage
from durus.persistent import Persistent
from durus.storage import get_reference_index, get_census
from durus.storage import gen_referring_oid_record, Storage
from durus.utils import p64
from popen2 import Popen4
from sancho.utest import UTest, raises
from time import sleep


class TestConnection (UTest):

    def _get_storage(self):
        return TempFileStorage()

    def check_connection(self):
        self.conn=conn=Connection(self._get_storage())
        self.root=root=conn.get_root()
        assert root._p_is_ghost() == True
        assert root is conn.get(p64(0))
        assert root is conn.get(0)
        assert conn is root._p_connection
        assert conn.get(p64(1)) == None
        conn.abort()
        conn.commit()
        assert root._p_is_ghost() == True
        root['a'] = Persistent()
        assert root._p_is_unsaved() == True
        assert root['a']._p_is_unsaved() == True
        root['a'].f=2
        assert conn.changed.values() == [root]
        conn.commit()
        assert root._p_is_saved()
        assert conn.changed.values() == []
        root['a'] = Persistent()
        assert conn.changed.values() == [root]
        root['b'] = Persistent()
        root['a'].a = 'a'
        root['b'].b = 'b'
        conn.commit()
        root['a'].a = 'a'
        root['b'].b = 'b'
        conn.abort()
        conn.shrink_cache()
        root['b'].b = 'b'
        del conn

    def check_shrink(self):
        storage = self._get_storage()
        self.conn=conn=Connection(storage, cache_size=3)
        self.root=root=conn.get_root()
        root['a'] = Persistent()
        root['b'] = Persistent()
        root['c'] = Persistent()
        assert self.root._p_is_unsaved()
        conn.commit()
        root['a'].a = 1
        conn.commit()
        root['b'].b = 1
        root['c'].c = 1
        root['d'] = Persistent()
        root['e'] = Persistent()
        root['f'] = Persistent()
        conn.commit()
        root['f'].f = 1
        root['g'] = Persistent()
        conn.commit()
        conn.pack()

    def check_storage_tools(self):
        connection = Connection(self._get_storage())
        root = connection.get_root()
        root['a'] = Persistent()
        root['b'] = Persistent()
        connection.commit()
        index = get_reference_index(connection.get_storage())
        assert index == {p64(1): [p64(0)], p64(2): [p64(0)]}
        census = get_census(connection.get_storage())
        assert census == {'PersistentDict':1, 'Persistent':2}
        references = list(gen_referring_oid_record(connection.get_storage(),
                                                   p64(1)))
        assert references == [(p64(0), connection.get_storage().load(p64(0)))]
        class Fake(object):
            pass
        s = Fake()
        s.__class__ = Storage
        raises(RuntimeError, s.__init__)
        raises(NotImplementedError, s.load, None)
        raises(NotImplementedError, s.begin)
        raises(NotImplementedError, s.store, None, None)
        raises(NotImplementedError, s.end)
        raises(NotImplementedError, s.sync)
        raises(NotImplementedError, s.gen_oid_record)


    def check_touch_every_reference(self):
        connection = Connection(self._get_storage())
        root = connection.get_root()
        root['a'] = Persistent()
        root['b'] = Persistent()
        from durus.persistent_list import PersistentList
        root['b'].c = PersistentList()
        connection.commit()
        touch_every_reference(connection, 'PersistentList')
        assert root['b']._p_is_unsaved()
        assert root['b'].c._p_is_unsaved()
        assert not root._p_is_unsaved()


class TestConnectionClientStorage (TestConnection):

    def _get_storage(self):
        return ClientStorage(port=self.port)

    def _pre(self):
        self.port = 9123
        self.server = Popen4('python %s --port=%s' % (
            run_durus.__file__, self.port))
        sleep(3) # wait for bind

    def _post(self):
        run_durus.stop_durus("", self.port)

    def check_conflict(self):
        b = Connection(self._get_storage())
        c = Connection(self._get_storage())
        rootb = b.get(p64(0))
        rootb['b'] = Persistent()
        rootc = c.get(p64(0))
        rootc['c'] = Persistent()
        c.commit()
        raises(ConflictError, b.commit)
        raises(KeyError, rootb.__getitem__, 'c')
        b.abort()
        assert rootb._p_is_ghost()
        rootc['d'] = Persistent()
        c.commit()
        rootb['d']

if __name__ == "__main__":
    TestConnection()
    TestConnectionClientStorage()
