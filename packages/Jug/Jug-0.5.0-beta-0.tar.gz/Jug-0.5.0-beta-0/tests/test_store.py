import jug.redis_store
import jug.file_based_store
import jug.dict_store
import pickle

def test_stores():
    def test_load_get(store):
        key = 'jugisbestthingever'
        assert not store.can_load(key)
        object = range(232)
        store.dump(object, key)
        assert store.can_load(key)
        assert store.load(key) == object
        store.remove(key)
        assert not store.can_load(key)
        store.close()
    def test_lock(store):
        key = 'jugisbestthingever'
        lock = store.getlock(key)
        assert not lock.is_locked()
        assert lock.get()
        assert not lock.get()
        lock2 = store.getlock(key)
        assert not lock2.get()
        lock.release()
        assert lock2.get()
        lock2.release()
        store.close()

    functions = (test_load_get, test_lock)
    stores = (lambda: jug.redis_store.redis_store('redis:'), lambda: jug.file_based_store.file_store('jugtest'), jug.dict_store.dict_store)
    for f in functions:
        for s in stores:
            yield f, s()

