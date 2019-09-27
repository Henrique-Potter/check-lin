from tools.runTests import run_tests
from tools.compileTests import compile_tests
from tools.createTests import create_tests
from tools.processStats import process_dir, stats_headers
from tools.processLinStats import process_lin_stats, lin_stats_headers

import argparse
import time
import os
import sys


min_depth = 1
max_depth = 5

# prepare result files
result_history = "results/table1.txt"
result_schedule = "results/table2.txt"
result_linear = "results/table3.txt"


# Other tests commented for a faster execution
BENCHMARKS =[
              ("ArrayBlockingQueue", "ABQ", "java.util.concurrent.ArrayBlockingQueue<Integer>")
              # ("ConcurrentHashMap", "CHM", "java.util.concurrent.ConcurrentHashMap<Integer,Integer>"),
              # ("ConcurrentLinkedDeque", "CLD", "java.util.concurrent.ConcurrentLinkedDeque<Integer>"),
              # ("ConcurrentLinkedQueue", "CLQ", "java.util.concurrent.ConcurrentLinkedQueue<Integer>"),
              # ("ConcurrentSkipListMap", "CSLM", "java.util.concurrent.ConcurrentSkipListMap<Integer,Integer>"),
              # ("ConcurrentSkipListSet", "CSLS", "java.util.concurrent.ConcurrentSkipListSet<Integer>"),
              # ("LinkedBlockingDeque", "LBD", "java.util.concurrent.ConcurrentLinkedDeque<Integer>"),
              # ("LinkedBlockingQueue", "LBQ", "java.util.concurrent.LinkedBlockingQueue<Integer>"),
              # ("LinkedTransferQueue", "LTQ", "java.util.concurrent.LinkedTransferQueue<Integer>"),
              # ("PriorityBlockingQueue", "PBQ", "java.util.concurrent.PriorityBlockingQueue<Integer>")
            ]


def main(selected_name):
    # prepare result files
    result_history = "results/table1.txt"
    result_schedule = "results/table2.txt"
    result_linear = "results/table3.txt"

    stats_headers(result_history, result_schedule)
    lin_stats_headers(result_linear)

    # 1. Create tests
    start_all = time.time()
    for (benchmark, name, classUnderTest) in BENCHMARKS:
        if selected_name and selected_name != name:
            continue

        startB = time.time()

        print("Creating linearizability checking tests for %s" % benchmark)

        stat_subdir = "stats%s" % (name, )
        create_tests(classUnderTest,
                     "example/histories/%s" % (benchmark, ),
                     "produced.test%s" % (name, ),
                     "Test%s" % (name, ),
                     stat_subdir,
                     "Stat%s" % (name, ),
                     min_depth, max_depth + 1)

        # History and Schedule Results
        print("Writing history and schedule results: [%s] -> [%s, %s]" % (benchmark, result_history, result_schedule))
        process_dir(name, os.path.join("stat", stat_subdir), result_history, result_schedule)

        # Compile and test the generated .java files
        for d in range(min_depth, max_depth + 1):
            print("Compiling linearizability checking tests: [%s] [d=%s]" % (benchmark, d))
            test_path = "produced/test{0}/D{1}".format(name, d)
            compile_tests(test_path)

            out_file = "out/{0}/D{1}.txt".format(name, d)
            print("Running linearizability checking tests:[%s] [d=%s]" % (benchmark, d))
            run_tests(test_path, out_file)

            # Count linearizable histories:
            process_lin_stats(name, out_file, d, result_linear)

        endB = time.time()

        elapsedSec = endB - startB
        print("The linearizability tests are generated, compiled and ran for the benchmark %s \n" % benchmark)
        print("All Seconds for checking %s: %s" % (benchmark, elapsedSec))
        print("All Minutes for checking %s: %s" % (benchmark, elapsedSec / 60))

    endAll = time.time()
    elapsedSec = endAll - start_all
    print("All Seconds for all benchmarks: %s" % elapsedSec)
    print("All Minutes for all benchnarks: %s" % (elapsedSec / 60))


def sbt_create_tests():

    # Prepare results file name
    stats_headers(result_history, result_schedule)
    lin_stats_headers(result_linear)

    start = time.time()

    for (benchmark, name, classUnderTest) in BENCHMARKS:

        print("Creating linearizability checking tests for %s" % benchmark)

        stat_subdir = "stats%s" % (name, )
        create_tests(classUnderTest,
                     "example/histories/%s" % (benchmark, ),
                     "produced.test%s" % (name, ),
                     "Test%s" % (name, ),
                     stat_subdir,
                     "Stat%s" % (name, ),
                     min_depth, max_depth + 1)

        # History and Schedule Results
        print("Writing history and schedule results: [%s] -> [%s, %s]" % (benchmark, result_history, result_schedule))
        process_dir(name, os.path.join("stat", stat_subdir), result_history, result_schedule)

    elapsed_secs = time.time() - start
    print("Test creation successful: %s" % elapsed_secs)


def sbt_compile_tests():

    start = time.time()
    for (benchmark, name, classUnderTest) in BENCHMARKS:
        # Compile and test the generated .java files
        for d in range(min_depth, max_depth + 1):
            print("Compiling linearizability checking tests: [%s] [d=%s]" % (benchmark, d))
            test_path = "produced/test{0}/D{1}".format(name, d)
            compile_tests(test_path)

    elapsed_secs = time.time() - start
    print("Java files compiled successfully: %s" % elapsed_secs)


def java_execute_tests():

    start = time.time()
    for (benchmark, name, classUnderTest) in BENCHMARKS:
        # Compile and test the generated .java files
        for d in range(min_depth, max_depth + 1):
            test_path = "produced/test{0}/D{1}".format(name, d)
            out_file = "out/{0}/D{1}.txt".format(name, d)
            print("Running Linearizability checking tests:[%s] [d=%s]" % (benchmark, d))
            run_tests(test_path, out_file)
    elapsed_secs = time.time() - start
    print("Java Linearizability tests successfully completed: %s" % elapsed_secs)
    print("Please call the appropriated command to plot results: %s" % elapsed_secs)


def plot_results():
    import matplotlib
    pass


if __name__ == '__main__':
    short_name = None
    if len(sys.argv) == 2:
        short_name = sys.argv[1]

    parser = argparse.ArgumentParser()
    parser.add_argument("operation", type=str, required=True)

    args = parser.parse_args()

    if args.operation == "sbt_create_tests":
        sbt_create_tests()
    if args.operation == "sbt_compile_tests":
        sbt_compile_tests()
    elif args.operation == "java_execute_tests":
        java_execute_tests()
    elif args.operation == "plot_tests":
        plot_results()

    #main(short_name)
