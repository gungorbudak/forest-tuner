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


def make_log_file(outputs_dir, stdout, stderr, label):
    logs_dir = os.path.join(outputs_dir, 'logs')
    if not os.path.exists(logs_dir):
        os.mkdir(logs_dir)
    log_file = os.path.join(logs_dir, 'log_' + label + '.txt')
    with open(log_file, 'w') as f:
        if stdout:
            f.write(stdout)
        if stderr:
            f.write(stderr)
    return


def make_network_file(outputs_dir, N, label, sif = True):
    extension = '.sif' if sif else '.tsv'
    network_file = os.path.join(outputs_dir, label + extension)
    with open(network_file, 'w') as f:
        for edge in N.edges():
            f.write(edge[0] + '\t' + edge[1] + '\n')
    return network_file


def get_label(prize_path, w, b):
    label = ''.join([
        os.path.splitext(os.path.basename(prize_path))[0], '_',
        'W', str(w), 'B', str(b)])
    return label


def get_configs(w, b, size):
    configs = []
    ws = np.linspace(w['start'], w['end'], size)
    bs = np.linspace(b['start'], b['end'], size)
    for i in xrange(size):
        for j in xrange(size):
            configs.append({
                # 'w': round(ws[i], 2),
                'w': ws[i],
                # 'b': round(bs[j], 2),
                'b': bs[j],
                'D': 10,
                'mu': 0.01
            })
    return configs


def get_network(network_file, sif = True):
    N = nx.Graph()
    target_index = 2 if sif else 1
    with open(network_file) as rows:
        for row in rows:
            cols = row.strip().split()
            N.add_edge(cols[0], cols[target_index])
    return N


def get_terminal_nodes(prize_path):
    nodes = set()
    with open(prize_path) as rows:
        for row in rows:
            cols = row.strip().split()
            nodes.add(cols[0])
    return nodes


def get_forest_feature(F):
    n1 = nx.number_connected_components(F)
    n2 = np.mean([T.size() for T in nx.connected_component_subgraphs(F)])
    return abs(n1 - n2)


def get_best_solution(solutions):
    min_feature = None
    best_solution = {}
    for solution in solutions:
        feature = get_forest_feature(solution['F'])
        if min_feature == None:
            min_feature = feature
            best_solution = solution
        else:
            if feature < min_feature:
                min_feature = feature
                best_solution = solution
    return best_solution


def run_forest_run(outputs_dir, forest_path, msgsteiner_path,
        prize_path, edge_path, config_file, label):
    optimal_forest_file = os.path.join(outputs_dir,
        label + '_optimalForest.sif')
    if not os.path.exists(optimal_forest_file):
        # create a command for running forest
        command = [
            'python', forest_path,
            '--msgpath', msgsteiner_path,
            '-p', prize_path,
            '-e', edge_path,
            '-c', config_file,
            '--outpath', outputs_dir,
            '--outlabel', label
        ]

        # run the command
        process = Popen(
            command,
            stdout=PIPE,
            stderr=PIPE,
            )
        stdout, stderr = process.communicate()

        # write output and errors to a log file
        make_log_file(outputs_dir, stdout, stderr, label)

        # delete all output files except optimal forest
        augmented_forest_file = os.path.join(outputs_dir,
            label + '_augmentedForest.sif')
        if os.path.exists(augmented_forest_file):
            os.remove(augmented_forest_file)

        dummy_forest_file = os.path.join(outputs_dir,
            label + '_dummyForest.sif')
        if os.path.exists(dummy_forest_file):
            os.remove(dummy_forest_file)

        edge_attributes_file = os.path.join(outputs_dir,
            label + '_edgeattributes.tsv')
        if os.path.exists(edge_attributes_file):
            os.remove(edge_attributes_file)

        node_attributes_file = os.path.join(outputs_dir,
            label + '_nodeattributes.tsv')
        if os.path.exists(node_attributes_file):
            os.remove(node_attributes_file)

        info_file = os.path.join(outputs_dir,
            label + '_info.txt')
        if os.path.exists(info_file):
            os.remove(info_file)

    # return the optimal forest file obtained for testing
    return optimal_forest_file


def main():
    # parsing terminal arguments
    parser = argparse.ArgumentParser(
        description='Prize-collecting Steiner Forest algorithm\
                     parameter tuner for w and b parameters',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--workingDir', metavar='DIR', default='.',
        help='Working directory for configs and outputs')
    parser.add_argument('--forestPath', metavar='FILE', required=True,
        help='(required) Absolute path to forest Python script')
    parser.add_argument('--msgsteinerPath', metavar='FILE', required=True,
        help='(required) Absolute path to msgsteiner executable')
    parser.add_argument('--prizePath', metavar='FILE', required=True,
        help='(required) Absolute path to prize file')
    parser.add_argument('--edgePath', metavar='FILE', required=True,
        help='(required) Absolute path to edge file')
    parser.add_argument('--wStart', metavar='DECIMAL',
        type=float, default=1.0,
        help='Starting value for w')
    parser.add_argument('--wEnd', metavar='DECIMAL',
        type=float, default=10.0,
        help='Ending value for w')
    parser.add_argument('--bStart', metavar='DECIMAL',
        type=float, default=1.0,
        help='Starting value for b')
    parser.add_argument('--bEnd', metavar='DECIMAL',
        type=float, default=10.0,
        help='Ending value for b')
    parser.add_argument('--size', metavar='INTEGER',
        type=int, default=10,
        help='Size of w and b values to tune for')
    parser.add_argument('--minNodes', metavar='INTEGER',
        type=int, default=60,
        help='Minimum percentage of nodes in optimal forests\
              overlapping with terminal nodes in prize file\
              to consider as a solution')
    args = parser.parse_args()

    if not os.path.isdir(args.workingDir):
        print 'The working directory {} is NOT a valid directory'.format(
            args.workingDir)
        raise SystemExit

    if not os.path.isfile(args.forestPath):
        print 'The forest path {} is NOT a valid file path'.format(
            args.forestPath)
        raise SystemExit

    if not os.path.isfile(args.msgsteinerPath):
        print 'The msgsteiner path {} is NOT a valid file path'.format(
            args.msgsteinerPath)
        raise SystemExit

    if not os.path.isfile(args.prizePath):
        print 'The prize path {} is NOT a valid file path'.format(
            args.prizePath)
        raise SystemExit

    if not os.path.isfile(args.edgePath):
        print 'The edge path {} is NOT a valid file path'.format(
            args.edgePath)
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
    print 'Running forest for {}'.format(args.prizePath)

    # list to collect optimal forests obtained
    results = []

    # run forest for each configuration obtained based on user input
    for config in configs:
        label = get_label(args.prizePath, config['w'], config['b'])
        config_file = make_config_file(args.workingDir, config, label)
        forest_file = run_forest_run(outputs_dir, args.forestPath,
            args.msgsteinerPath, args.prizePath, args.edgePath,
            config_file, label)
        results.append({
            'config': config,
            'forest_file': forest_file
            })

    # read terminal nodes from the prize file
    terminal_nodes = get_terminal_nodes(args.prizePath)
    terminal_nodes_size = float(len(terminal_nodes))

    # collect the solutions under certain conditions
    solutions = []
    for result in results:
        F = get_network(result['forest_file'])
        # don't include forests with less than given number of edges
        if F.number_of_edges() > 0:
            # only if more than 60 percent of terminal nodes
            # are present in the solution
            overlap = 100 * (len(terminal_nodes.intersection(F.nodes())) /
                terminal_nodes_size)
            if overlap > args.minNodes:
                solutions.append({
                    'config': result['config'],
                    'F': F
                    })

    # get the best solution based on number of trees
    # and average size of trees in the optimal forests
    # and write the best solution to a text file
    solution = get_best_solution(solutions)
    label = get_label(args.prizePath,
        solution['config']['w'], solution['config']['b'])
    forest_file = make_network_file(outputs_dir, solution['F'],
        label + '_bestOptimalForest', sif = False)
    print 'Best config. found to be {}'.format(', '.join([
        k + ': ' + str(v) for k, v in solution['config'].iteritems()]))
    print 'Best solution written to {}'.format(forest_file)


if __name__ == '__main__':
    main()
