from generator_tools.copygenerators import*

import unittest
import test_support

def copytest(n=2, raises = None, fun_args = (), kwd_args = {}):
    name = []
    def test(method):
        def test_wrap(self):
            f = method(self)
            gen_f = f(*fun_args, **kwd_args)
            for i in range(n):
                gen_f.next()
            if raises:
                self.assertRaises(raises, copy_generator, gen_f)
            else:
                gen_g = copy_generator(gen_f)
                self.assertEqual(list(gen_g),list(gen_f))
        test_wrap.__name__ = method.__name__
        return test_wrap
    return test

class TestSimpleSequence(unittest.TestCase):

    @copytest(2)
    def test_three_yields(self):
        def f():
            k = 0
            yield k
            k+=1
            yield k
            k+=1
            yield k
        return f

class TestNestedWhileLoop(unittest.TestCase):

    @copytest(2)
    def test_nested_while_0(self):
        def f():
            k = 0
            while k<30:
                yield k
                k+=1
        return f

    @copytest(5)
    def test_while_sequence_5(self):
        def f():
            k = 0
            while k<3:
                yield k
                k+=1
            while k<6:
                yield k
                k+=1
            while k<9:
                yield k
                k+=1
        return f

    @copytest(7)
    def test_while_sequence_7(self):
        def f():
            k = 0
            while k<3:
                yield k
                k+=1
            while k<6:
                yield k
                k+=1
            while k<9:
                yield k
                k+=1
        return f

    @copytest(2)
    def test_nested_while_1(self):
        def f():
            k = 0
            while k<5:
                yield k
                j = 0
                while j<10:
                    yield (k,j)
                    j+=1
                k+=1
        return f

    @copytest(3)
    def test_nested_while_2(self):
        def f():
            k = 0
            while k<4:
                yield k
                j = 0
                while j<2:
                    yield k,j
                    i = 0
                    while i<2:
                        yield k,j,i
                        i+=1
                    j+=1
                k+=1
        return f


    @copytest(3)
    def test_nested_while_6(self):
        def f():
            k = 0
            while k<8:
                while k<7:
                    while k<6:
                        while k<5:
                            while k<4:
                                while k<3:
                                    while k<2:
                                        k+=1
                                        yield k
                                    k+=1
                                    yield k
                                k+=1
                                yield k
                            k+=1
                            yield k
                        k+=1
                        yield k
                    k+=1
                    yield k
                k+=1
                yield k
        return f

class TestTryStmt(unittest.TestCase):
    @copytest(2)
    def test_simple_try_stmt(self):
        def f():
            try:
                yield 0
                yield 1
                yield 2
                1/0
            except ZeroDivisionError:
                pass
        return f

    @copytest(3)
    def test_nested_try_stmt(self):
        def f():
            k = 0
            try:
                yield 0
                try:
                    yield 1
                    yield 2
                    k.bla
                except AttributeError:
                    pass
                yield 3
                1/0
            except ZeroDivisionError:
                yield 4
        return f

    @copytest(3)
    def _test_try_finally(self):
        def f():
            k = 0
            try:
                yield 0
                yield 1
                k.bla
            except AttributeError:
                yield 2
                yield 3
            finally:
                yield 5
            yield 4
        return f

    @copytest(3)
    def test_try_while(self):
        def f():
            k = 0
            try:
                while k<2:
                    yield k
                    yield k+1
                    k+=1
                yield 2
                1/0
            except ZeroDivisionError:
                pass
        return f

    @copytest(3)
    def test_while_try_while(self):
        def f():
            k = 0
            while k<10:
                try:
                    while k<2:
                        yield k
                        yield k+1
                        k+=1
                    k+=1
                    yield 2
                    if k == 7:
                        1/0
                except ZeroDivisionError:
                    break
        return f

class TestForStmt(unittest.TestCase):
    @copytest(raises = CopyGeneratorException)
    def test_unpolished_for(self):
        def f():
            for i in range(10):
                yield i
        return f

    @copytest(3)
    def test_simple_for(self):
        def f():
            r = for_iter(range(10))
            for i in r:
                yield i
        return f

    @copytest(raises = CopyGeneratorException)
    def test_one_unpolished(self):
        def f():
            r = for_iter(range(10))
            for i in r:
                yield i
            for i in range(10):
                yield i
        return f

    @copytest(77)
    def test_nested_for(self):
        def f():
            r1 = for_iter(range(10))
            for i in r1:
                r2 = for_iter(range(10))
                for j in r2:
                    yield i+j
        return f

    @copytest(77)
    def test_deep_nesting(self):
        def f():
            r1 = for_iter(range(2))
            for i1 in r1:
                r2 = for_iter(range(2))
                for i2 in r2:
                    r3 = for_iter(range(2))
                    for i3 in r3:
                        r4 = for_iter(range(2))
                        for i4 in r4:
                            r5 = for_iter(range(2))
                            for i5 in r5:
                                r6 = for_iter(range(2))
                                for i6 in r6:
                                    r7 = for_iter(range(2))
                                    for i7 in r7:
                                        yield i1+i2+i3+i4+i5+i6+i7
        return f

class TestForAndWhileStmt(unittest.TestCase):
    @copytest(9)
    def test_for_while(self):
        def f():
            r = for_iter(range(7))
            for i in r:
                j = 0
                while j<5:
                    yield i+j
                    j+=1
                yield i-j
        return f

    @copytest(9)
    def test_while_for(self):
        def f():
            j = 0
            while True:
                r = for_iter(range(7))
                for i in r:
                    yield i+j
                j+=1
                yield i-j
                if j == 5:
                    break
        return f

class TestForAndWhileStmtWithAddArgs(unittest.TestCase):
    @copytest(9, fun_args = (3,4))
    def test_fun_args(self):
        def f(x,y):
            r = for_iter(range(7))
            for i in r:
                j = 0
                while j<5:
                    yield i+j+x
                    j+=1
                yield i-j-y
        return f

    @copytest(9, fun_args = (3,4), kwd_args = {"a":9})
    def test_fun_and_kwd_args(self):
        def f(x,y,a):
            r = for_iter(range(7))
            for i in r:
                j = 0
                while j<5:
                    yield i+j+x
                    j+=1
                yield i-j-y-a
        return f

class TestMultipleGenerators(unittest.TestCase):
    @copytest(20, fun_args = (3,4))
    def test_fun_args(self):
        def g(x,y):
            r = for_iter(range(7))
            for i in r:
                j = 0
                while j<5:
                    yield i+j+x
                    j+=1
                yield i-j-y

        def f(x,y):
            r = for_iter(g(4,5))
            for i in r:
                j = 0
                while j<5:
                    yield i+j+x
                    j+=1
                yield i-j-y

        return f

    @copytest(15, fun_args = (3,4))
    def test_multi_gen1(self):
        def g(x,y):
            r = for_iter(range(x,y))
            for i in r:
                yield i

        def f(x,y):
            G = for_iter([g(0,7), g(7,14), g(14, 21)])
            for h in G:
                H = for_iter(h)
                for item in H:
                    yield item
        return f

    @copytest(20, fun_args = (3,4))
    def test_multi_gen2(self):
        def g(x,y):
            r = for_iter(range(7))
            for i in r:
                yield i+x+y

        def f(x,y):
            G = for_iter(g(i,j) for i in [1,2] for j in [3,4])
            for h in G:
                H = for_iter(h)
                for item in H:
                    yield item + x + y
        return f

    @copytest(5, fun_args = (3,4))
    def test_multi_gen2(self):
        def g(x,y):
            r = for_iter(range(7))
            for i in r:
                yield i+x+y

        def f(x,y):
            G = for_iter(g(i,j) for i in [1,2] for j in [3,4])
            for h in G:
                H = for_iter(h)
                for item in H:
                    yield item + x + y
        return f

class TestMultipleCopies(unittest.TestCase):

    def test_multiple_copies(self):
        def f(x):
            r = for_iter(range(x))
            for i in r:
                yield i

        gen_f = f(10)
        gen_f.next()
        gen_f.next()
        gen_g = copy_generator(gen_f)
        gen_h = copy_generator(gen_f)
        l_g = list(gen_g)
        l_h = list(gen_h)
        l_f = list(gen_f)
        self.assertEqual(l_g, l_h)
        self.assertEqual(l_g, l_f)

    def test_copy_of_copy(self):
        def f(x):
            r = for_iter(range(x))
            for i in r:
                yield i

        gen_f = f(10)
        gen_f.next()
        gen_f.next()
        gen_g = copy_generator(gen_f)
        gen_g.next()
        gen_f.next()
        gen_h = copy_generator(gen_g)
        l_g = list(gen_g)
        l_h = list(gen_h)
        l_f = list(gen_f)
        self.assertEqual(l_g, l_h)
        self.assertEqual(l_g, l_f)

    def test_clone_1(self):
        def f(x):
            r = for_iter(range(x))
            for i in r:
                yield i

        gen_f = f(10)
        gen_g = copy_generator(gen_f)
        gen_h = copy_generator(gen_g)
        l_g = list(gen_g)
        l_h = list(gen_h)
        self.assertEqual(l_g, l_h)

    def test_clone_2(self):
        def f(x):
            r = for_iter(range(x))
            for i in r:
                yield i

        gen_f = f(10)
        gen_f.next()
        gen_f.next()
        gen_f.next()
        gen_g = copy_generator(gen_f)
        gen_h = copy_generator(gen_g)
        l_g = list(gen_g)
        l_h = list(gen_h)
        self.assertEqual(l_g, l_h)


    def test_clone_4(self):
        def f(x):
            r = for_iter(range(x))
            for i in r:
                yield i

        gen_f = f(10)
        gen_f.next()
        gen_f.next()
        gen_f.next()
        gen_g = copy_generator(gen_f)
        gen_h = copy_generator(gen_g)
        gen_h.next()
        gen_k = copy_generator(gen_h)
        l_h = list(gen_h)
        l_k = list(gen_k)
        self.assertEqual(l_h, l_k)

    def test_chain_of_copies(self):
        def f(x):
            r = for_iter(range(x))
            for i in r:
                yield i

        gen_f = f(10)
        gen_f.next()
        gen_g = copy_generator(gen_f)
        gen_g.next()
        gen_h = copy_generator(gen_g)
        gen_h.next()
        gen_k = copy_generator(gen_h)
        self.assertEqual(gen_k.next(), gen_h.next())

    def test_clone_3(self):
        def f(x):
            r = for_iter(range(x))
            for i in r:
                yield i

        gen_f = f(10)
        gen_f.next()
        gen_f.next()
        gen_f.next()
        gen_g = copy_generator(gen_f)
        gen_h = copy_generator(gen_g)
        gen_k = copy_generator(gen_h)
        gen_m = copy_generator(gen_k)
        l_g = list(gen_g)
        l_h = list(gen_h)
        l_k = list(gen_k)
        l_m = list(gen_m)
        self.assertEqual(l_g, l_h)
        self.assertEqual(l_h, l_k)
        self.assertEqual(l_k, l_m)

def test_main():
    test_support.run_unittest(TestNestedWhileLoop)
    test_support.run_unittest(TestTryStmt)
    test_support.run_unittest(TestForStmt)
    test_support.run_unittest(TestForAndWhileStmt)
    test_support.run_unittest(TestForAndWhileStmtWithAddArgs)
    test_support.run_unittest(TestMultipleGenerators)
    test_support.run_unittest(TestMultipleCopies)

if __name__ == "__main__":
    test_main()

