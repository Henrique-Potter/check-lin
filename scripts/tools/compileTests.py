import os
import sys
from os import path


def compile_tests(tests_path):
    # print("Compiling tests in [%s]..." % (tests_path, ))
    # print(tests_path)

    all_filesto_compile = ""

    for filename in os.listdir(tests_path):
        if not filename.endswith(".java"):
            continue

        java_file = path.join(tests_path, filename)
        # print("Compiling: %s" % (java_file,))
        all_filesto_compile = ''.join((all_filesto_compile, ' ', java_file))

    return all_filesto_compile

    #call("javac {0}".format(all_filesto_compile), shell=True)


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Please specify the directory of test files")
        sys.exit()

    compile_tests(sys.argv[1])
