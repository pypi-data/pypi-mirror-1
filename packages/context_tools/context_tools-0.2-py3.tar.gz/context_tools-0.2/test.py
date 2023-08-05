import unittest

import context_tools


class Object(object):
    pass


class Test_decorate_with(unittest.TestCase):
    def test_pass_attributes_through(self):
        called = {"enter": 0, "exit": 0}
        class Manager(object):
            def __enter__(mgr):
                called["enter"] += 1
                return 7
            def __exit__(mgr, exc_type, exc_val, exc_tb):
                self.assertEqual(exc_type, None)
                self.assertEqual(exc_val, None)
                self.assertEqual(exc_tb, None)
                called["exit"] += 1

        def set_foo(func):
            func.foo = 5
            return func

        @context_tools.decorate_with(Manager())
        @set_foo
        def foo():
            pass
        self.assertEqual(foo.foo, 5)

    def test_normal_operation(self):
        called = {"enter": 0, "exit": 0}
        class Manager(object):
            def __enter__(mgr):
                called["enter"] += 1
                return 7
            def __exit__(mgr, exc_type, exc_val, exc_tb):
                self.assertEqual(exc_type, None)
                self.assertEqual(exc_val, None)
                self.assertEqual(exc_tb, None)
                called["exit"] += 1

        @context_tools.decorate_with(Manager())
        def f(context):
            self.assertEqual(context, 7)
            self.assertEqual(called["enter"], 1)
            self.assertEqual(called["exit"], 0)
        f()
        self.assertEqual(called["enter"], 1)
        self.assertEqual(called["exit"], 1)

    def test_raise_pass_through(self):
        called = {"enter": 0, "exit": 0}
        class Manager(object):
            def __enter__(mgr):
                called["enter"] += 1
                return 7
            def __exit__(mgr, exc_type, exc_val, exc_tb):
                self.assertEqual(exc_type, RuntimeError)
                self.failUnless(isinstance(exc_val, RuntimeError))
                self.assertNotEqual(exc_tb, None)
                called["exit"] += 1

        @context_tools.decorate_with(Manager())
        def f(context):
            self.assertEqual(context, 7)
            self.assertEqual(called["enter"], 1)
            self.assertEqual(called["exit"], 0)
            raise RuntimeError()
        try:
            f()
        except RuntimeError:
            pass
        else:
            self.fail("Failed to raise RuntimeError")
        self.assertEqual(called["enter"], 1)
        self.assertEqual(called["exit"], 1)

    def test_swallow_exception(self):
        called = {"enter": 0, "exit": 0}
        class Manager(object):
            def __enter__(mgr):
                called["enter"] += 1
                return 7
            def __exit__(mgr, exc_type, exc_val, exc_tb):
                self.assertEqual(exc_type, RuntimeError)
                self.failUnless(isinstance(exc_val, RuntimeError))
                self.assertNotEqual(exc_tb, None)
                called["exit"] += 1
                return True

        @context_tools.decorate_with(Manager())
        def f(context):
            self.assertEqual(context, 7)
            self.assertEqual(called["enter"], 1)
            self.assertEqual(called["exit"], 0)
            raise RuntimeError()
        f()
        self.assertEqual(called["enter"], 1)
        self.assertEqual(called["exit"], 1)


class Test_yield_with(unittest.TestCase):
    def test_pass_attributes_through(self):
        called = {"enter": 0, "exit": 0}
        class Manager(object):
            def __enter__(mgr):
                called["enter"] += 1
                return 7
            def __exit__(mgr, exc_type, exc_val, exc_tb):
                self.assertEqual(exc_type, None)
                self.assertEqual(exc_val, None)
                self.assertEqual(exc_tb, None)
                called["exit"] += 1

        def set_foo(func):
            func.foo = 5
            return func

        @context_tools.yield_with(Manager())
        @set_foo
        def foo(context):
            yield 5
        self.assertEqual(foo.foo, 5)

    def test_normal_operation(self):
        called = {"enter": 0, "exit": 0}
        class Manager(object):
            def __enter__(mgr):
                called["enter"] += 1
                return 7
            def __exit__(mgr, exc_type, exc_val, exc_tb):
                self.assertEqual(exc_type, None)
                self.assertEqual(exc_val, None)
                self.assertEqual(exc_tb, None)
                called["exit"] += 1

        @context_tools.yield_with(Manager())
        def f(context):
            self.assertEqual(context, 7)
            yield 6
            yield 7

        gen = f()
        self.assertEqual(next(gen), 6)
        self.assertEqual(called["enter"], 1)
        self.assertEqual(called["exit"], 0)
        self.assertEqual(next(gen), 7)
        self.assertEqual(called["enter"], 1)
        self.assertEqual(called["exit"], 0)
        try:
            next(gen)
        except StopIteration:
            self.assertEqual(called["enter"], 1)
            self.assertEqual(called["exit"], 1)
        else:
            self.fail("Failed to raise StopIteration")

    def test_swallow_exception(self):
        called = {"enter": 0, "exit": 0}
        class Manager(object):
            def __enter__(mgr):
                called["enter"] += 1
                return 7
            def __exit__(mgr, exc_type, exc_val, exc_tb):
                self.assertEqual(exc_type, RuntimeError)
                self.failUnless(isinstance(exc_val, RuntimeError))
                self.assertNotEqual(exc_tb, None)
                called["exit"] += 1
                return True

        @context_tools.yield_with(Manager())
        def f(context):
            self.assertEqual(context, 7)
            yield 6
            yield 7
            raise RuntimeError()

        gen = f()
        self.assertEqual(next(gen), 6)
        self.assertEqual(called["enter"], 1)
        self.assertEqual(called["exit"], 0)
        self.assertEqual(next(gen), 7)
        self.assertEqual(called["enter"], 1)
        self.assertEqual(called["exit"], 0)
        next(gen)
        self.assertEqual(called["enter"], 1)
        self.assertEqual(called["exit"], 1)

    def test_raise(self):
        called = {"enter": 0, "exit": 0}
        class Manager(object):
            def __enter__(mgr):
                called["enter"] += 1
                return 7
            def __exit__(mgr, exc_type, exc_val, exc_tb):
                self.assertEqual(exc_type, RuntimeError)
                self.failUnless(isinstance(exc_val, RuntimeError))
                self.assertNotEqual(exc_tb, None)
                called["exit"] += 1

        @context_tools.yield_with(Manager())
        def f(context):
            self.assertEqual(context, 7)
            yield 6
            yield 7
            raise RuntimeError()

        gen = f()
        self.assertEqual(next(gen), 6)
        self.assertEqual(called["enter"], 1)
        self.assertEqual(called["exit"], 0)
        self.assertEqual(next(gen), 7)
        self.assertEqual(called["enter"], 1)
        self.assertEqual(called["exit"], 0)
        try:
            next(gen)
        except RuntimeError:
            self.assertEqual(called["enter"], 1)
            self.assertEqual(called["exit"], 1)
        else:
            self.fail("Failed to raise exception")


class Test_test_with(unittest.TestCase):
    def test(self):
        called = {"enter": 0, "exit": 0}
        class Manager(object):
            def __enter__(mgr):
                called["enter"] += 1
                return 7
            def __exit__(mgr, exc_type, exc_val, exc_tb):
                self.assertEqual(exc_type, None)
                self.assertEqual(exc_val, None)
                self.assertEqual(exc_tb, None)
                called["exit"] += 1

        obj = Object()
        set_up, tear_down = context_tools.test_with(foo=Manager(),
                                                    bar=Manager())
        self.assertEqual(called["enter"], 0)
        self.assertEqual(called["exit"], 0)
        set_up(obj)
        self.assertEqual(called["enter"], 2)
        self.assertEqual(called["exit"], 0)
        self.assertEqual(obj.foo, 7)
        self.assertEqual(obj.bar, 7)
        tear_down(obj)
        self.assertEqual(called["enter"], 2)
        self.assertEqual(called["exit"], 2)


if __name__ == "__main__":
    unittest.main()
