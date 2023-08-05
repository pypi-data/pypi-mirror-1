#
# Run tests in the modules of this sub-package
#

from processing import activeChildren, freezeSupport, HAVE_NATIVE_SEMAPHORE


def run_test(module, types):
    for type in types:
        if type == 'processes+server':
            print '\n\n------ %s using processes and server process ------\n' \
                  % module.__name__
        elif type == 'processes':
            print '\n\n------ %s using processes ------\n' \
                  % module.__name__
        elif type == 'threads':
            print '\n\n------ %s using threads ------\n' % module.__name__
        else:
            raise ValueError

        module.config = type
        reload(module)
        module.test()


def main():
    from processing.test import test_processing, test_newtype, \
         test_doc, test_speed, test_connection, test_reduction, test_stop

    old_processes = set(activeChildren())

    run_test(test_doc, ['processes+server', 'threads'])
    run_test(test_connection, ['processes', 'threads'])
    run_test(test_newtype, ['processes', 'threads'])
    run_test(test_reduction, ['processes', 'threads'])
    run_test(test_stop, ['processes'])

    if HAVE_NATIVE_SEMAPHORE:
        from processing.test import test_workers, test_pool
        run_test(test_processing, ['processes', 'processes+server', 'threads'])
        run_test(test_workers, ['processes'])
        run_test(test_pool, ['processes'])
    else:
        run_test(test_processing, ['processes+server', 'threads'])

    processes = set(activeChildren())
    assert processes.issubset(old_processes)

if __name__ == '__main__':
    freezeSupport()
    main()
