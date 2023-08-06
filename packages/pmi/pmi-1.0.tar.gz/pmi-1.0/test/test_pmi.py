import pmi
import unittest
from cPickle import PicklingError

# On the frontend
if __name__ != 'pmi':
    # load the module on all workers
    pmi.execfile_(__file__)

# Mock functions, visible to worker and frontend
def mockFunc(arg=None, *args, **kwds):
    global mockFuncCalled, mockFuncArg, mockFuncArgs, mockFuncKwds
    mockFuncCalled = True
    mockFuncArg = arg
    mockFuncArgs = args
    mockFuncKwds = kwds
    return 42

def add(a, b):
    return a + b

# Mock function, visible only to the workers
if __name__ == 'pmi':
    def mockFunc2(arg=None, *args, **kwds):
        global mockFunc2Called, mockFunc2Arg, mockFunc2Args, mockFunc2Kwds
        mockFunc2Called = True
        mockFunc2Arg = arg
        mockFunc2Args = args
        mockFunc2Kwds = kwds
        return 52

else:
    # test pmi calls
    class TestCall(unittest.TestCase):
        def tearDown(self):
            pmi.sync()

        def testBuiltinFunction(self):
            self.assertEqual(pmi.call(zip), [])
            # by string
            self.assertEqual(pmi.call('zip'), [])

        def testFunction(self):
            global mockFuncCalled

            self.assertEqual(pmi.call(mockFunc), 42)
            self.assert_(mockFuncCalled)

            self.assertFalse('mockFunc2' in globals())
            self.assertEqual(pmi.call('mockFunc2'), 52)
            self.assert_(pmi.mockFunc2Called)
            self.assertFalse('mockFunc2' in globals())

        def testBadArgument(self) :
            if pmi.isController:
                self.assertRaises(TypeError, pmi.call, 1)
                self.assertRaises(ValueError, pmi.call, lambda x: x)
                self.assertRaises(NameError, pmi.call, 'doesntexist')

    # test passing arguments to a pmi call
    class TestPassArguments(unittest.TestCase):
        def setUp(self):
            global mockFuncArg, mockFuncArgs, mockFuncKwds
            mockFuncArg = None
            mockFuncArgs = None
            mockFuncKwds = None

        def tearDown(self):
            pmi.sync()

        def testSimple(self):
            global mockFuncArg
            pmi.call(mockFunc, 42)
            self.assertEqual(mockFuncArg, 42)
            self.assertEqual(mockFuncArgs, ())
            self.assertEqual(mockFuncKwds, {})

        def testList(self):
            global mockFuncArg, mockFuncArgs
            pmi.call(mockFunc, 42, 52, 62)
            self.assertEqual(mockFuncArg, 42)
            self.assertEqual(mockFuncArgs, (52, 62))
            self.assertEqual(mockFuncKwds, {})

        def testKeywords(self) :
            global mockFuncArg, mockFuncArgs, mockFuncKwds
            pmi.call(mockFunc, arg1=42, arg2=52)
            self.assertEqual(mockFuncArg, None)
            self.assertEqual(mockFuncArgs, ())
            self.assertEqual(mockFuncKwds, {'arg1' : 42, 'arg2' : 52})

        def testMixed(self) :
            global mockFuncArg, mockFuncArgs, mockFuncKwds
            pmi.call(mockFunc, 42, 52, 62, arg1=72, arg2=82)
            self.assertEqual(mockFuncArg, 42)
            self.assertEqual(mockFuncArgs, (52, 62))
            self.assertEqual(mockFuncKwds, {'arg1' : 72, 'arg2' : 82})

        def testController(self):
            global mockFuncArg, mockFuncArgs, mockFuncKwds
            obj = pmi.call(mockFunc, arg=42, __pmictr_arg=52)
            if pmi.isController:
                self.assertEqual(mockFuncArg, 52)
            else:
                self.assertEqual(mockFuncArg, 42)

        def testNonPicklable(self):
            if pmi.isController:
                self.assertRaises(PicklingError, pmi.call, mockFunc, arg=lambda x: x)

    # test pmi invoke
    class TestInvoke(unittest.TestCase) :
        def testFunction(self):
            res = pmi.invoke(mockFunc)
            if pmi.isController:
                self.assertEqual(list(res), [42 for x in res])
            else:
                self.assertEqual(res, None)

    # test pmi reduce
    class TestReduce(unittest.TestCase):
        def testBadArgument(self):
            if pmi.isController :
                self.assertRaises(pmi.UserError, pmi.reduce, mockFunc)

        def testFunction(self):
            res = pmi.reduce(add, mockFunc)
            if pmi.isController :
                self.assertEqual(res, 42*pmi.size)
            else :
                self.assertEqual(res, None)

            # by string
            res = pmi.reduce('add', mockFunc)
            if pmi.isController :
                self.assertEqual(res, 42*pmi.size)
            else :
                self.assertEqual(res, None)

        def testLambda(self) :
            pmi.exec_('myadd = lambda a,b: a+b')

            res = pmi.reduce('myadd', mockFunc)
            if pmi.isController :
                self.assertEqual(res, 42*pmi.size)
            else :
                self.assertEqual(res, None)

            pmi.exec_('del myadd')

    class TestExec(unittest.TestCase) :
        def testImportModule(self) :
            pmi.exec_("import random")
            # check that it's loaded into pmi
            self.assert_(hasattr(pmi, 'random'))
            # check that the main namespace is not polluted
            try :
                exec 'n=random.__name__'
                self.fail("expected a NameError")
            except NameError :
                pass
            else :
                self.fail("expected a NameError")
            # clean up
            pmi.exec_("del(random)")
            # check that it's gone
            self.assertFalse(hasattr(pmi, 'random'))

        def testImportModuleAs(self) :
            pmi.exec_("import random as s")
            # check that it's loaded
            self.assert_(hasattr(pmi, 's'))
            self.assertEqual(pmi.s.__name__, "random")
            # clean up
            pmi.exec_("del(s)")

## Mock Classes
# This class is visible to all workers and the frontend
class MockClass(object):
    delCalled = False
    def __init__(self, arg=None, *args, **kwds):
        self.fCalled = False
        MockClass.delCalled = False

    def __del__(self):
        if hasattr(MockClass, 'delCalled'):
            MockClass.delCalled = True

    def f(self, arg=None, *args, **kwds):
        self.fCalled = True
        return 42

mockClassDelCalled = False

class MockOSClass:
    pass

if __name__ == 'pmi':
    # This class is visible only to the workers
    class MockClass2(object):
        def f(self, arg=None, *args, **kwds):
            return 52
else:
    ## Test Cases
    class TestPMIClass(unittest.TestCase) :
        def setUp(self):
            global mockFuncArg, mockFuncArgs, mockFuncKwds
            mockFuncArg = None
            mockFuncArgs = None
            mockFuncKwds = None

        def tearDown(self):
            pmi.sync()

        def testCreateByClass(self) :
            if pmi.isController:
                obj = pmi.create(MockClass)
            else:
                # on the workers, don't use an argument to make sure
                # that it is not used 
                obj = pmi.create()
            # test whether the class has been initialized correctly 
            # (on all workers)
            self.assert_(isinstance(obj, MockClass))

            # delete object
            del(obj)
            pmi.sync()
            self.assert_(MockClass.delCalled)

        def testCreateByString(self) :
            obj = pmi.create("MockClass2")
            self.assertEqual(obj.__class__.__name__, "MockClass2")

            # delete object
            del(obj)
            pmi.sync()

            # Test that MockClass2 has not been pulled into the scripts namespace
            self.assertFalse('MockClass2' in globals())

        def testCreateBadArgument(self):
            if pmi.isController :
                self.assertRaises(TypeError, pmi.create, MockOSClass)
                self.assertRaises(ValueError, pmi.create, 1)
                self.assertRaises(pmi.UserError, pmi.create)

        def testCallMethod(self):
            # call via instance
            obj = pmi.create(MockClass)
            self.assertEqual(pmi.call(obj.f), 42)
            self.assert_(obj.fCalled)

            # call via class
            obj2 = pmi.create(MockClass)
            self.assertFalse(obj2.fCalled)
            self.assertEqual(pmi.call(MockClass.f, obj2), 42)
            self.assert_(obj2.fCalled)

            # call via string
            obj3 = pmi.create('MockClass2')
            self.assertEqual(pmi.call('MockClass2.f', obj3), 52)

            # call via instance and method name
            obj4 = pmi.create(MockClass)
            self.assertEqual(pmi.call(obj4, 'f'), 42)
            self.assert_(obj4.fCalled)

        def testPMIClassArgument(self):
            global mockFuncArg, mockFuncArgs
            obj = pmi.create(MockClass)
            self.assert_(isinstance(obj, MockClass))

            # pass the PMI class as argument and its id
            pmi.call(mockFunc, obj, id(obj))

            # on all workers, obj should now be in the object
            self.assertEqual(mockFuncArg, obj)
            # but it should not have the same id on all workers!
            if pmi.isController:
                self.assertEqual(mockFuncArgs[0], id(obj))
            else:
                self.assertNotEqual(mockFuncArgs[0], id(obj))

    class TestCommunicationFailure(unittest.TestCase) :
        def testCommandMismatch(self):
            if pmi.isController :
                pmi.exec_('pass')
            else :
                self.assertRaises(pmi.UserError, pmi.call, None)

        def testMPIandPMI(self) :
            if pmi.isController:
                try:
                    # import MPI
                    from mpi4py import MPI
                    MPI.COMM_WORLD.bcast(1, root=pmi.CONTROLLER)
                    MPI.COMM_WORLD.bcast((1,2), root=pmi.CONTROLLER)
                    MPI.COMM_WORLD.bcast({'bla':'blub'}, root=pmi.CONTROLLER)
                except ImportError:
                    import boostmpi as mpi
                    mpi.world.broadcast(value=1, root=pmi.CONTROLLER)
                    mpi.world.broadcast(value=(1,2), root=pmi.CONTROLLER)
                    mpi.world.broadcast(value={'bla':'blub'}, root=pmi.CONTROLLER)
            else :
                self.assertRaises(pmi.UserError, pmi.exec_)
                self.assertRaises(pmi.UserError, pmi.exec_)
                self.assertRaises(pmi.UserError, pmi.exec_)

    class TestWrongCommands(unittest.TestCase) :
        def testReceiveOnController(self) :
            if pmi.isController:
                self.assertRaises(pmi.UserError, pmi.receive)
                self.assertRaises(pmi.UserError, pmi.exec_)
                self.assertRaises(pmi.UserError, pmi.create)
                self.assertRaises(pmi.UserError, pmi.invoke)
                self.assertRaises(pmi.UserError, pmi.call)
                self.assertRaises(pmi.UserError, pmi.reduce)

        def testBadOnWorker(self):
            if pmi.isWorker:
                self.assertRaises(pmi.UserError, pmi.finalizeWorkers)
                self.assertRaises(pmi.UserError, pmi.stopWorkerLoop)
                self.assertRaises(pmi.UserError, pmi.registerAtExit)

class MockProxyLocal(object):
    delCalled = False
    def __init__(self, arg=None, *args, **kwds):
        self.x = 17
        self.arg = arg
        self.args = args
        self.kwds = kwds
        MockProxyLocal.delCalled = False
    def __del__(self):
        if hasattr(MockProxyLocal, 'delCalled'):
            MockProxyLocal.delCalled = True
    def f(self):
        self.called = "f"
        return 42
    def f2(self):
        self.called = "f2"
        return 52
    def f3(self):
        self.called = "f3"
        return 62
    def f4(self):
        self.called = "f4"
        return 72

    def setX(self, v):
        self._x = v
    def getX(self):
        return self._x
    x = property(getX, setX)

if __name__ != 'pmi':

    if pmi.isController:
        class MockProxy(object):
            __metaclass__ = pmi.Proxy
            pmiproxydefs = dict(
                cls = 'MockProxyLocal',
                localcall = [ 'f' ],
                pmicall = [ 'f2' ],
                pmiinvoke = [ 'f3' ],
                pmiproperty = [ 'x' ]
                )
            def f4(self):
                return pmi.call(self, 'f4')

    class TestProxyCreateAndDelete(unittest.TestCase):
        def testCreateandDelete(self):
            if pmi.isController:
                obj = MockProxy()
                self.assert_(hasattr(obj, 'pmiobject'))
                self.assert_(isinstance(obj.pmiobject, pmi.MockProxyLocal))
                self.assert_(hasattr(obj, 'pmiinit'))
                del(obj)
            else:
                pmiobj = pmi.create()
                self.assert_(isinstance(pmiobj, pmi.MockProxyLocal))
                del(pmiobj)

            pmi.sync()
            self.assert_(pmi.MockProxyLocal.delCalled)
        
    class TestProxy(unittest.TestCase) :
        def setUp(self):
            global mockFuncArg
            mockFuncArg = None

            if pmi.isController:
                self.obj = MockProxy()
                self.pmiobj = self.obj.pmiobject
            else:
                self.pmiobj = pmi.create()

        def tearDown(self):
            if pmi.isController:
                del(self.obj)
            pmi.sync()

        def testLocalCall(self):
            if pmi.isController:
                self.assertEqual(self.obj.f(), 42)
                pmi.sync()
                self.assertEqual(self.pmiobj.called, 'f')
            else:
                self.assertFalse(hasattr(self.pmiobj, 'called'))
                pmi.sync()

        def testCall(self):
            if pmi.isController:
                self.assertEqual(self.obj.f2(), 52)
            else:
                self.assertEqual(pmi.call(), 52)
            self.assertEqual(self.pmiobj.called, 'f2')

        def testInvoke(self):
            if pmi.isController:
                res = self.obj.f3()
                self.assertEqual(list(res), [62 for x in res])
            else:
                self.assertEqual(pmi.invoke(), None)
            self.assertEqual(self.pmiobj.called, 'f3')

        def testCallViaSelf(self):
            if pmi.isController:
                self.assertEqual(self.obj.f4(), 72)
            else:
                self.assertEqual(pmi.call(), 72)
            self.assertEqual(self.pmiobj.called, 'f4')
            
        def testProperty(self):
            if pmi.isController:
                self.obj.x = 42
                self.assertEqual(self.obj.x, 42)
            else:
                pmi.call()
            self.assertEqual(self.pmiobj.x, 42)

        def testProxyArgument(self):
            global mockFuncArg
            if pmi.isController:
                pmi.call(mockFunc, self.obj)
            else:
                pmi.call()
            self.assertEqual(mockFuncArg, self.pmiobj)

        
    class TestModifiedProxy(unittest.TestCase):
        def testUserSuppliedInit(self):
            if pmi.isController:
                class MockProxy(object):
                    __metaclass__ = pmi.Proxy
                    pmiproxydefs = dict(cls='MockProxyLocal')

                    def __init__(self, arg):
                        self.arg = arg
                        self.pmiinit(arg+10)

                obj = MockProxy(42)
                pmiobj = obj.pmiobject
                self.assert_(hasattr(obj, 'arg'))
                self.assertEqual(obj.arg, 42)
                self.assert_(isinstance(pmiobj, pmi.MockProxyLocal))
                self.assertEqual(pmiobj.arg, 52)
                del(pmiobj)
                del(obj)
                pmi.sync()
            else:
                pmiobj = pmi.create()
                self.assert_(isinstance(pmiobj, pmi.MockProxyLocal))
                self.assertEqual(pmiobj.arg, 52)
                del(pmiobj)
                pmi.sync()

        def testUserSuppliedFunction(self):
            if pmi.isController:
                class MockProxy(object):
                    __metaclass__ = pmi.Proxy
                    pmiproxydefs = dict(cls='MockProxyLocal')

                    def f4(self):
                        self.pmiobject.called = "f4"
                        return 72

                obj = MockProxy()
                pmiobj = obj.pmiobject
                self.assertEqual(obj.f4(), 72)
                pmi.sync()
                self.assertEqual(pmiobj.called, 'f4')
                del(obj)
                pmi.sync()
            else:
                pmiobj = pmi.create()
                pmi.sync()
                self.assertFalse(hasattr(pmiobj, 'called'))
                pmi.sync()


class MockProxyLocalBase(object):
    def f(self, arg=None):
        self.arg = arg
        self.fCalled = True

    def g(self, arg=None):
        self.gArg = arg

class MockProxyLocalDerived(MockProxyLocalBase):
    def f(self, arg2=None, arg=42):
        self.arg2 = arg2
        self.fDerivedCalled = True
        MockProxyLocalBase.f(self, arg)

if __name__ != 'pmi':

    if pmi.isController:
        class MockProxyAbstractBase(object):
            __metaclass__ = pmi.Proxy
            pmiproxydefs = dict(pmicall=['f', 'g'])

        class MockProxyDerived(MockProxyAbstractBase):
            __metaclass__ = pmi.Proxy
            pmiproxydefs = dict(cls='MockProxyLocalDerived')

    class TestProxyHierarchy(unittest.TestCase):
        def testCreate(self):
            if pmi.isController:
                obj = MockProxyDerived()
                pmiobj = obj.pmiobject
                self.assert_(hasattr(obj, 'f'))
                self.assert_(hasattr(obj, 'g'))
                self.assert_(isinstance(pmiobj, pmi.MockProxyLocalDerived))
            else:
                pmiobj = pmi.create()
                self.assert_(isinstance(pmiobj, pmi.MockProxyLocalDerived))

        def testCallInherited(self):
            if pmi.isController:
                obj = MockProxyDerived()
                pmiobj = obj.pmiobject
                obj.g(42)
            else:
                pmiobj = pmi.create()
                pmi.call()

            self.assertEqual(pmiobj.gArg, 42)

        def testCallOverridden(self):
            if pmi.isController:
                obj = MockProxyDerived()
                pmiobj = obj.pmiobject
                obj.f(52)
            else:
                pmiobj = pmi.create()
                pmi.call()

            self.assert_(hasattr(pmiobj, 'fDerivedCalled'))
            self.assert_(hasattr(pmiobj, 'fCalled'))
            self.assertEqual(pmiobj.arg, 42)
            self.assertEqual(pmiobj.arg2, 52)

        def testCallRedefined(self):
            if pmi.isController:
                class MockProxyDerived(MockProxyAbstractBase):
                    __metaclass__ = pmi.Proxy
                    pmiproxydefs = dict(cls='MockProxyLocalDerived', 
                                        localcall=['f'])
            
                obj = MockProxyDerived()
                pmiobj = obj.pmiobject
                obj.f(52)
                self.assert_(hasattr(pmiobj, 'fDerivedCalled'))
                self.assert_(hasattr(pmiobj, 'fCalled'))
                self.assertEqual(pmiobj.arg, 42)
                self.assertEqual(pmiobj.arg2, 52)
            else:
                pmiobj = pmi.create()
                self.assertFalse(hasattr(pmiobj, 'fDerivedCalled'))
                self.assertFalse(hasattr(pmiobj, 'fCalled'))

if __name__ != 'pmi':
    import os
    logConfigFile = 'log.conf'
    if os.path.exists(logConfigFile):
        import logging.config
        logging.config.fileConfig(logConfigFile)
    else: print("Didn't read log.conf")

    unittest.main()

