#!/usr/bin/env python
from main import *

def main(argv):

    test_id = "20191001_050822"
    test_log_name = "test_" + test_id + ".log"
    log_file = CPII_TESTLOG + "/" + test_log_name

    total_individuals = output_generations(test_id, log_file, GEN)
    plot_result(test_id, GEN, total_individuals)  # (optional) plot individuals

if __name__ == '__main__':
    main(sys.argv)
