from functest import reports
import sys

class MyReport(reports.FunctestReportInterface):
    def summary(self, test_list, totals_dict, stdout_capture):
        sys.__stdout__.write("all tests list "+str(test_list)+'\n')
        sys.__stdout__.write('--stdout--'+stdout_capture)
        sys.__stdout__.flush()
    def test_function(self, test_function):
        sys.__stdout__.write("Finished test_function: "+test_function.__name__)
    def setup_module(self, test_function):
        sys.__stdout__.write("Finished setup_module: "+test_function.__name__)
    def teardown_module(self, test_function):
        sys.__stdout__.write("Finished teardown_module: "+test_function.__name__)
    

reports.register_reporter(MyReport())

def test_stub():
    print 'capture in stdout'

def setup_module(module): pass
def teardown_module(module): pass
