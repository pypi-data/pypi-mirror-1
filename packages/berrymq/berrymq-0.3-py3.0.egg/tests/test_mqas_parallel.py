# -*- coding: utf-8 -*-

mqas = None
import time


def test_thread_pool_create1():
    try:
        mqas.ThreadPool.make_thread_pool(-1)
    except ValueError:
        pass
    else:
        raise RuntimeError("ValueError should be raised")
    print("mqas: test_thread_pool_create1() OK!")


def test_thread_pool_create2():
    mqas.ThreadPool.make_thread_pool(5)
    assert len(mqas.ThreadPool._pool) == 5
    assert mqas.ThreadPool.empty() == False
    mqas.ThreadPool.stop_thread_pool()
    assert len(mqas.ThreadPool._pool) == 0
    assert mqas.ThreadPool.empty() == True
    print("mqas: test_thread_pool_create2() OK!")


def test_thread_pool_recreate1():
    mqas.ThreadPool.make_thread_pool(3)
    assert len(mqas.ThreadPool._pool) == 3
    mqas.ThreadPool.make_thread_pool(5)
    assert len(mqas.ThreadPool._pool) == 5
    mqas.ThreadPool.stop_thread_pool()
    assert len(mqas.ThreadPool._pool) == 0
    print("mqas: test_thread_pool_recreate1() OK!")


def test_thread_pool_recreate2():
    mqas.ThreadPool.make_thread_pool(5)
    assert len(mqas.ThreadPool._pool) == 5
    mqas.ThreadPool.make_thread_pool(5)
    assert len(mqas.ThreadPool._pool) == 5
    mqas.ThreadPool.stop_thread_pool()
    assert len(mqas.ThreadPool._pool) == 0
    print("mqas: test_thread_pool_recreate2() OK!")


def test_thread_pool_recreate3():
    mqas.ThreadPool.make_thread_pool(5)
    assert len(mqas.ThreadPool._pool) == 5
    mqas.ThreadPool.make_thread_pool(3)
    time.sleep(1)
    mqas.ThreadPool.clear_thread_pool()
    assert len(mqas.ThreadPool._pool) == 3
    mqas.ThreadPool.stop_thread_pool()
    assert len(mqas.ThreadPool._pool) == 0
    print("mqas: test_thread_pool_recreate3() OK!")


def test_followers_works_parallely1():
    """parallel test(not parallel version)
    """
    call_history = []
    @mqas.auto_twitter("sample1:entry")
    def exp():
        call_history.append("exp_1")
        time.sleep(3)
        call_history.append("exp_2")

    @mqas.following_function("sample1:entry")
    def com1(message):
        time.sleep(1)
        call_history.append("com1_1")
        time.sleep(3)
        call_history.append("com1_2")

    @mqas.following_function("sample1:entry")
    def com2(message):
        time.sleep(2)
        call_history.append("com2_1")
        time.sleep(3)
        call_history.append("com2_2")

    exp()
    assert call_history == ["com1_1", "com1_2", "com2_1",
                            "com2_2", "exp_1", "exp_2"]
    print("mqas: test_followers_works_parallely1() OK!")


def test_followers_works_parallely2():
    """parallel test

          0. 1. 2. 3. 4. 5.
    exp : *        *
    com1:    *        *
    com2:       *        *
    """
    mqas.set_multiplicity(3)
    call_history = []
    @mqas.auto_twitter("sample2:entry")
    def exp():
        call_history.append("exp_1")
        time.sleep(3)
        call_history.append("exp_2")


    @mqas.following_function("sample2:entry")
    def com1(message):
        time.sleep(1)
        call_history.append("com1_1")
        time.sleep(3)
        call_history.append("com1_2")

    @mqas.following_function("sample2:entry")
    def com2(message):
        time.sleep(2)
        call_history.append("com2_1")
        time.sleep(3)
        call_history.append("com2_2")

    exp()
    time.sleep(4)
    mqas.set_multiplicity(0)
    #print(call_history)
    assert call_history == ["exp_1", "com1_1", "com2_1",
                            "exp_2", "com1_2", "com2_2"]
    print("mqas: test_followers_works_parallely2() OK!")


def test(mqas_module):
    global mqas
    mqas = mqas_module
    test_thread_pool_create1()
    test_thread_pool_create2()
    test_thread_pool_recreate1()
    test_thread_pool_recreate2()
    test_thread_pool_recreate3()
    test_followers_works_parallely1()
    test_followers_works_parallely2()
