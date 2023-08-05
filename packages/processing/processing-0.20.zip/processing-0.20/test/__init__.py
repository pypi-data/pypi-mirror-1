#
# This module contains the function 'main()' which will run the
# modules 'test_processing' and 'test_newtype' using both processes
# and threads.
#

def main():
    from processing.test import test_processing
    test_processing.use_dummy = False
    reload(test_processing)
    print "\n\n-------- RUNNING test_processing USING PROCESSES --------"
    test_processing.main()

    test_processing.use_dummy = True
    reload(test_processing)
    print "\n\n-------- RUNNING test_processing USING THREADS --------"
    test_processing.main()


    from processing.test import test_newtype
    test_newtype.use_dummy = False
    reload(test_newtype)
    print "\n\n-------- RUNNING test_newtype USING PROCESSES --------"
    test_newtype.main()

    test_newtype.use_dummy = True
    reload(test_newtype)
    print "\n\n-------- RUNNING test_newtype USING THREADS --------"
    test_newtype.main()


    from processing.test import test_doc
    print "\n\n-------- RUNNING test_doc --------"
    test_doc.main()

if __name__ == '__main__':
    main()
