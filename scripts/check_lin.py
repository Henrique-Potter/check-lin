from tools.runTests import run_tests
from tools.compileTests import compile_tests
from tools.createTests import create_tests
from tools.processStats import process_dir, stats_headers
from tools.processLinStats import process_lin_stats, lin_stats_headers
from pathlib import Path


import argparse
import time
import os
import sys


curr_dir = Path(os.path.realpath(__file__)).parents[1]

min_depth = 1
max_depth = 5

# prepare result files
result_history = curr_dir.joinpath("results/table1.txt")
result_schedule = curr_dir.joinpath("results/table2.txt")
result_linear = curr_dir.joinpath("results/table3.txt")

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
        process_dir(name, os.path.join(curr_dir, "stat", stat_subdir), result_history, result_schedule)

    elapsed_secs = time.time() - start
    print("Test creation successful: %s" % elapsed_secs)


def sbt_compile_tests():

    start = time.time()
    for (benchmark, name, classUnderTest) in BENCHMARKS:
        # Compile and test the generated .java files
        for d in range(min_depth, max_depth + 1):
            print("Compiling linearizability checking tests: [%s] [d=%s]" % (benchmark, d))
            test_path = "produced/test{0}/D{1}".format(name, d)
            compile_tests(curr_dir.joinpath(test_path))

    elapsed_secs = time.time() - start
    print("Java files compiled successfully: %s" % elapsed_secs)


def java_execute_tests():

    start = time.time()
    for (benchmark, name, classUnderTest) in BENCHMARKS:
        # Compile and test the generated .java files
        for d in range(min_depth, max_depth + 1):

            test_path = curr_dir
            java_class_path = "produced/test{0}/D{1}".format(name, d)
            out_file = curr_dir.joinpath("out/{0}/D{1}.txt".format(name, d))
            print("Running Linearizability checking tests:[%s] [d=%s]" % (benchmark, d))

            run_tests(java_class_path, test_path, out_file)

            # Count linearizable histories:
            process_lin_stats(name, out_file, d, result_linear)

    elapsed_secs = time.time() - start
    print("Java Linearizability tests successfully completed: %s" % elapsed_secs)
    print("Please execute the operation \"plot_results\" to plot results")


def set_project_root():
    for path in Path.cwd().parents:
        if path.name == 'check_lin':
            return path


def plot_results():
    import matplotlib.pyplot as plt

    header = None
    deph_data = []
    found_lin = []

    with open(result_linear, "r") as stats:
        for line in stats:
            values = line.split("\t")
            if values[0] == "name":
                header = line[1:]
            elif values[0] == "ABQ":
                deph_data.append(values[3].strip())
                found_lin.append(values[4].strip())

    plt.bar(deph_data, found_lin, align='center', alpha=0.5)
    #plt.xticks(y_pos, objects)
    plt.ylabel('# Linerializable Traces')
    plt.xlabel('Hitting Families Depth (D)')

    plt.title('Linearizability Checking Results')

    plt.show()


# Cleans all the extra files generated by running the experiment operations
def clean_all():
    import shutil

    produced_folder = curr_dir.joinpath("produced")
    project_folder = curr_dir.joinpath("project")
    results_folder = curr_dir.joinpath("results")
    stat_folder = curr_dir.joinpath("stat")
    target_folder = curr_dir.joinpath("target")
    out_folder = curr_dir.joinpath("out")

    if os.path.exists(produced_folder):
        print("The folder \"produced\" was successfully deleted!")
        shutil.rmtree(produced_folder)

    if os.path.exists(project_folder):
        print("The folder \"project\" was successfully deleted!")
        shutil.rmtree(project_folder)

    if os.path.exists(results_folder):
        print("The folder \"results\" was successfully deleted!")
        shutil.rmtree(results_folder)

    if os.path.exists(stat_folder):
        print("The folder \"stat\" was successfully deleted!")
        shutil.rmtree(stat_folder)

    if os.path.exists(target_folder):
        print("The folder \"target\" was successfully deleted!")
        shutil.rmtree(target_folder)

    if os.path.exists(out_folder):
        print("The folder \"out\" was successfully deleted!")
        shutil.rmtree(out_folder)


if __name__ == '__main__':
    short_name = None
    if len(sys.argv) == 2:
        short_name = sys.argv[1]

    parser = argparse.ArgumentParser()
    parser.add_argument("-o", "--operation", help="Please, specify one operation!", type=str, required=True)

    args = parser.parse_args()

    if args.operation == "sbt_create_tests":
        sbt_create_tests()
    elif args.operation == "sbt_compile_tests":
        sbt_compile_tests()
    elif args.operation == "java_execute_tests":
        java_execute_tests()
    elif args.operation == "plot_results":
        plot_results()
    elif args.operation == "clean_all":
        clean_all()
    else:
        print("The operation {} does not exist. Please make sure that you are using the correct operation.".format(args.operation))
