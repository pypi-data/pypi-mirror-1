import juglib.task
def add1(x):
    return x + 1
def add2(x):
    return x + 2

def _assert_tsorted(tasks):
    for i in xrange(len(tasks)):
        for j in xrange(i+1,len(tasks)):
            for dep in list(tasks[i].dependencies) + tasks[i].kwdependencies.values():
                if type(dep) is list:
                    assert tasks[j] not in dep
                else:
                    assert tasks[j] is not dep
            
def test_topological_sort():
    bases = [juglib.task.Task(add1,i) for i in xrange(10)]
    derived = [juglib.task.Task(add1,t) for t in bases]
    derived2 = [juglib.task.Task(add1,t) for t in derived]
    derived3 = [juglib.task.Task(add1,t) for t in derived]
    
    alltasks = bases + derived
    juglib.task.topological_sort(alltasks)
    _assert_tsorted(alltasks)
    
    alltasks.reverse()
    juglib.task.topological_sort(alltasks)
    _assert_tsorted(alltasks)

    alltasks = bases + derived
    alltasks.reverse()
    juglib.task.topological_sort(alltasks)
    _assert_tsorted(alltasks)

    alltasks = derived + bases
    juglib.task.topological_sort(alltasks)
    _assert_tsorted(alltasks)

    alltasks = derived + bases + derived2
    juglib.task.topological_sort(alltasks)
    _assert_tsorted(alltasks)

    alltasks = derived + bases + derived2 + derived3
    juglib.task.topological_sort(alltasks)
    _assert_tsorted(alltasks)

def test_topological_sort_kwargs():
    def add2(x):
        return x + 2
    def sumlst(lst,param):
        return sum(lst)

    bases = [juglib.task.Task(add2,x=i) for i in xrange(10)]
    derived = [juglib.task.Task(sumlst,lst=bases,param=p) for p in xrange(4)]

    alltasks = bases + derived
    juglib.task.topological_sort(alltasks)
    _assert_tsorted(alltasks)
    
    alltasks.reverse()
    juglib.task.topological_sort(alltasks)
    _assert_tsorted(alltasks)

    alltasks = bases + derived
    alltasks.reverse()
    juglib.task.topological_sort(alltasks)
    _assert_tsorted(alltasks)

    alltasks = derived + bases
    juglib.task.topological_sort(alltasks)
    _assert_tsorted(alltasks)


def test_load_after_run():
    T = juglib.task.Task(add1,1)
    T.run()
    assert T.can_load()

def test_hash_same_func():
    T0 = juglib.task.Task(add1,0)
    T1 = juglib.task.Task(add1,1)

    assert T0._filename(hash_only=True) != T1._filename(hash_only=True)
    assert T0._filename(hash_only=False) != T1._filename(hash_only=False)
    
def test_hash_different_func():
    T0 = juglib.task.Task(add1,0)
    T1 = juglib.task.Task(add2,0)

    assert T0._filename(hash_only=True) != T1._filename(hash_only=True)
    assert T0._filename(hash_only=False) != T1._filename(hash_only=False)

