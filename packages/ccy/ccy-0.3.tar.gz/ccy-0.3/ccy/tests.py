import unittest
import testcases

def run():
    loader = unittest.TestLoader()
    suite  = loader.loadTestsFromModule(testcases)
    runner = unittest.TextTestRunner()
    runner.run(suite)
        
        
if __name__ == '__main__':
    run()