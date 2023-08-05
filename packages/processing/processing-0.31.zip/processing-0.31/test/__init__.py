#
# Run tests in the modules of this sub-package
#

def run_test(module, types):
    for type in types:
        if type == 'normal':
            print '\n\n------ %s using processes ------\n' % \
                  module.__name__
        elif type == 'local':
            print '\n\n------ %s using processes, shared memory ------\n' % \
                  module.__name__
        elif type == 'dummy':
            print '\n\n------ %s using threads ------\n' % module.__name__
        else:
            raise ValueError
        
        module.manager_type = type
        reload(module)
        module.test()

def main():
    from processing.test import test_processing, test_newtype, \
         test_doc, test_speed, test_connection, test_reduction, test_stop
    from processing import Process

    
    run_test(test_doc, ['normal', 'dummy'])
    run_test(test_connection, ['normal', 'dummy'])
    run_test(test_newtype, ['normal', 'dummy'])
    run_test(test_reduction, ['normal', 'dummy'])
    
    try:
        from processing._processing import Blocker
    except ImportError:
        run_test(test_processing, ['normal', 'dummy'])
    else:
        run_test(test_processing, ['normal', 'local', 'dummy'])

    if hasattr(Process, 'stop'):
        run_test(test_stop, ['normal'])
    else:
        print '\n\n------ processing.test_stop skipped ------\n'
    
if __name__ == '__main__':
    main()
