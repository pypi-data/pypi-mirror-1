tdfw = None
import random

class TestResult(metaclass=tdfw.Follower):
    @tdfw.following_method("unittest", "good_result")
    @tdfw.expose_method("unittest", "record_test_result")
    def record_good_result(self, ticket):
        tdfw.twitter("unittest", "record_test_result")

    @tdfw.following_method("unittest", "bad_result")
    @tdfw.expose_method("unittest", "record_test_result")
    def record_bad_result(self, ticket):
        tdfw.twitter("unittest", "record_test_result")

    @tdfw.following_method("unittest", "finish_test")
    @tdfw.expose_method("unittest", "summarize_result")
    def record_result(self, ticket):
        tdfw.twitter("unittest", "summarize_result")


class TestRunner(metaclass=tdfw.Follower):
    @tdfw.expose_method("unittest", "ready_to_run")
    @tdfw.expose_method("unittest", "finish_test")
    @tdfw.following_method("unittest", "finish_test_collect")
    def ready_to_run(self):
        tdfw.twitter("unittest", "ready_to_run")
        tdfw.twitter("unittest", "finish_test")

    @tdfw.expose_method("unittest", "finish_init")
    def initialize(self):
        tdfw.twitter("unittest", "finish_init")


class ConsoleOutputter(metaclass=tdfw.Follower):
    @tdfw.following_method("unittest", "record_test_result")
    def print_each_result(self, ticket):
        pass

    @tdfw.following_method("unittest", "summarize_result")
    def print_summary(self, ticket):
        pass


class TestCollector(metaclass=tdfw.Follower):
    @tdfw.following_method("unittest", "finish_init")
    @tdfw.expose_method("unittest", "finish_test_collect")
    def collect_test_cases(self):
        tdfw.twitter("unittest", "finish_test_collect")


class TestCase(metaclass=tdfw.Follower):
    @tdfw.following_method("unittest", "ready_to_run")
    @tdfw.expose_method("unittest", "good_result")
    @tdfw.expose_method("unittest", "bad_result")
    def run_test(self, ticket):
        tdfw.twitter("unittest", random.choice(["good_result", "bad_result"]))

def test(tdfw_module):
    global tdfw
    tdfw = tdfw_module
    from pprint import pprint

    result = TestResult()
    runner = TestRunner()
    outputter = ConsoleOutputter()
    collector = TestCollector()
    tests = []
    for i in range(5):
        tests.append(TestCase())

    #print("expositions")
    pprint(tdfw.show_expositions())

    #print("followingments")
    #pprint(tdfw.show_followingments())

    #print(tdfw.show_network())
