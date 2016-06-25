import os
import argparse
import numpy as np
import networkx as nx
from csv import DictReader
from subprocess import Popen, PIPE


def make_config_file(working_dir, config, label):
    configs_dir = os.path.join(working_dir, 'configs')
    if not os.path.exists(configs_dir):
        os.mkdir(configs_dir)
    config_file = os.path.join(configs_dir, 'config_' + label + '.txt')
    if not os.path.exists(config_file):
        with open(config_file, 'w') as f:
            for k, v in config.iteritems():
                f.write(k + ' = ' + str(v) + '\n')
    return config_file


def make_log_file(outputs_dir, stdin, stdout, label):
    logs_dir = os.path.join(outputs_dir, 'logs')
    if not os.path.exists(logs_dir):
        os.mkdir(logs_dir)
    log_file = os.path.join(logs_dir, 'log_' + label + '.txt')
    with open(log_file, 'w') as f:
        if stdin:
            f.write(stdin)
        if stdout:
            f.write(stdout)
    return


def make_forest_file(outputs_dir, forest, label):
    forest_file = os.path.join(outputs_dir, label + '_bestOptimalForest.tsv')
    with open(forest_file, 'w') as f:
        for edge in forest.edges():
            f.write(edge[0] + '\t' + edge[1] + '\n')
    return forest_file


def get_label(prize_file, w, b):
    label = ''.join([
        os.path.splitext(os.path.basename(prize_file))[0], '_',
        'W', str(w), 'B', str(b)])
    return label


def get_configs(w, b, size):
    configs = []
    ws = np.linspace(w['start'], w['end'], size)
    bs = np.linspace(b['start'], b['end'], size)
    for i in xrange(size):
        for j in xrange(size):
            configs.append({
                'w': ws[i],
                'b': bs[j],
                'D': 10,
                'mu': 0.01
            })
    return configs


def get_forest(forest_file):
    F = nx.Graph()
    with open(forest_file) as rows:
        for row in rows:
            cols = row.strip().split()
            F.add_edge(cols[0], cols[2])
    return F


def get_forest_feature(F):
    n1 = nx.number_connected_components(F)
    n2 = np.mean([T.size() for T in nx.connected_component_subgraphs(F)])
    return abs(n1 - n2)


def get_best_solution(solutions):
    min_feature = None
    best_solution = {}
    for solution in solutions:
        feature = get_forest_feature(solution['forest'])
        if min_feature == None:
            min_feature = feature
            best_solution = solution
        else:
            if feature < min_feature:
                min_feature = feature
                best_solution = solution
    return best_solution


def run_forest_run(outputs_dir, forest_path, msgsteiner_path,
        prizes_file, edges_file, config_file, label):
    # create a command for running forest
    command = [
        'python', forest_path,
        '--msgpath', msgsteiner_path,
        '-p', prizes_file,
        '-e', edges_file,
        '-c', config_file,
        '--outpath', outputs_dir,
        '--outlabel', label
    ]

    # run the command
    process = Popen(
        command,
        stdin=PIPE,
        stdout=PIPE,
        )
    stdin, stdout = process.communicate()

    # write output and errors to a log file
    make_log_file(outputs_dir, stdin, stdout, label)

    # delete all output files except optimal forest
    augmented_forest_file = os.path.join(outputs_dir, label + '_augmentedForest.sif')
    if os.path.exists(augmented_forest_file):
        os.remove(augmented_forest_file)

    dummy_forest_file = os.path.join(outputs_dir, label + '_dummyForest.sif')
    if os.path.exists(dummy_forest_file):
        os.remove(dummy_forest_file)

    edge_attributes_file = os.path.join(outputs_dir, label + '_edgeattributes.tsv')
    if os.path.exists(edge_attributes_file):
        os.remove(edge_attributes_file)

    node_attributes_file = os.path.join(outputs_dir, label + '_nodeattributes.tsv')
    if os.path.exists(node_attributes_file):
        os.remove(node_attributes_file)

    info_file = os.path.join(outputs_dir, label + '_info.txt')
    if os.path.exists(info_file):
        os.remove(info_file)

    # return the optimal forest obtained for testing
    return os.path.join(outputs_dir, label + '_optimalForest.sif')


def main():
    # parsing terminal arguments
    parser = argparse.ArgumentParser(
        description='Prize-collecting Steiner Forest algorithm\
                     parameter tuner for w and b parameters',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--workingDir', default='.',
        help='Working directory for configs and outputs')
    parser.add_argument('--forestPath', required=True,
        help='Absolute path to forest Python script')
    parser.add_argument('--msgsteinerPath', required=True,
        help='Absolute path to msgsteiner executable')
    parser.add_argument('--prizePath', required=True,
        help='Absolute path to prize file')
    parser.add_argument('--edgePath', required=True,
        help='Absolute path to edge file')
    parser.add_argument('--wStart', type=float, default=1.0,
        help='Starting value for w')
    parser.add_argument('--wEnd', type=float, default=10.0,
        help='Ending value for w')
    parser.add_argument('--bStart', type=float, default=1.0,
        help='Starting value for b')
    parser.add_argument('--bEnd', type=float, default=10.0,
        help='Ending value for b')
    parser.add_argument('--size', type=int, default=10,
        help='Size of w and b values to tune for')
    args = parser.parse_args()

    if not os.path.isdir(args.workingDir):
        print 'The working directory {} is NOT a valid directory'.format(args.workingDir)
        raise SystemExit

    if not os.path.isfile(args.forestPath):
        print 'The forest path {} is NOT a valid file path'.format(args.forestPath)
        raise SystemExit

    if not os.path.isfile(args.msgsteinerPath):
        print 'The msgsteiner path {} is NOT a valid file path'.format(args.msgsteinerPath)
        raise SystemExit

    if not os.path.isfile(args.prizePath):
        print 'The prize path {} is NOT a valid file path'.format(args.prizePath)
        raise SystemExit

    if not os.path.isfile(args.edgePath):
        print 'The edge path {} is NOT a valid file path'.format(args.edgePath)
        raise SystemExit

    # get configurations based on user input
    configs = get_configs(
        {'start': args.wStart, 'end': args.wEnd},
        {'start': args.bStart, 'end': args.bEnd},
        args.size)

    # directory for storing outputs
    outputs_dir = os.path.join(args.workingDir, 'outputs')
    if not os.path.exists(outputs_dir):
        os.mkdir(outputs_dir)
    print 'Running forest for', args.prizePath

    # list to collect optimal forests obtained
    results = []

    # run forest for each configuration obtained based on user input
    for config in configs:
        label = get_label(args.prizePath, config['w'], config['b'])
        config_file = make_config_file(args.workingDir, config, label)
        forest_file = run_forest_run(outputs_dir, args.forestPath,
            args.msgsteinerPath, args.prizePath, args.edgePath, config_file, label)
        results.append({
            'config': config,
            'forest_file': forest_file
            })

    # collect the solutions with at least one edge
    solutions = []
    for result in results:
        F = get_forest(result['forest_file'])
        if F.number_of_edges() > 0:
            solutions.append({
                'config': result['config'],
                'forest': F
                })

    # get the best solution based on number of trees
    # and avg size of trees in the optimal forests
    # and write the best solution to a text file
    solution = get_best_solution(solutions)
    label = get_label(args.prizePath, solution['config']['w'], solution['config']['b'])
    forest_file = make_forest_file(outputs_dir, solution['forest'], label)
    print 'Best config', ', '.join([
        k + ': ' + str(v) for k, v in solution['config'].iteritems()])
    print 'Best solution written to', forest_file


if __name__ == '__main__':
    main()
