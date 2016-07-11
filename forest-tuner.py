import os
import argparse
import logging
import numpy as np
import networkx as nx
import multiprocessing as mp
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
    if not os.path.exists(network_file):
        with open(network_file, 'w') as f:
            for edge in N.edges():
                f.write(edge[0] + '\t' + edge[1] + '\n')
    return network_file


def get_label(prize_path, w, b, mu):
    label = ''.join([
        os.path.splitext(os.path.basename(prize_path))[0], '_',
        'w', str(w), 'b', str(b), 'mu', str(mu)])
    return label


def get_configs(w, b, mu, size):
    configs = []
    ws = np.linspace(w['start'], w['end'], size)
    bs = np.linspace(b['start'], b['end'], size)
    mus = np.linspace(mu['start'], mu['end'], size)
    for i in xrange(size):
        for j in xrange(size):
            for k in xrange(size):
                configs.append({
                    'w': round(ws[i], 2),
                    'b': round(bs[j], 2),
                    'mu': round(mus[k], 2),
                    'D': 10
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


def get_solutions(results, prize_path, min_nodes):
    # read terminal nodes from the prize file
    terminal_nodes = get_terminal_nodes(prize_path)
    terminal_nodes_size = float(len(terminal_nodes))

    solutions = []
    for result in results:
        F = get_network(result['forest_file'])
        # don't include forests with less than given number of edges
        if F.number_of_edges() > 0:
            # only if more than given percent of terminal nodes
            # are present in the solution
            overlap = 100 * (len(terminal_nodes.intersection(F.nodes())) /
                terminal_nodes_size)
            if overlap > min_nodes:
                solutions.append({
                    'config': result['config'],
                    'F': F
                    })
    return solutions


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


def forest_worker(job):
    # local variables for the job
    working_dir = job['working_dir']
    forest_path = job['forest_path']
    msgsteiner_path = job['msgsteiner_path']
    prize_path = job['prize_path']
    edge_path = job['edge_path']
    outputs_dir = job['outputs_dir']
    config = job['config']
    label = job['label']

    # generate a config file
    config_file = make_config_file(working_dir, config, label)

    # determine name of the result file
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

        # suffixes for output files to be deleted
        suffixes = [
            '_augmentedForest.sif',
            '_dummyForest.sif',
            '_edgeattributes.tsv',
            '_nodeattributes.tsv',
            '_info.txt',
        ]

        # delete all output files except optimal forest
        for suffix in suffixes:
            output_file = os.path.join(outputs_dir, label + suffix)
            if os.path.exists(output_file):
                os.remove(output_file)

    # return the config and
    # optimal forest file obtained for testing
    return {'config': config, 'forest_file': optimal_forest_file}


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
    parser.add_argument('--muStart', metavar='DECIMAL',
        type=float, default=0.0,
        help='Starting value for mu')
    parser.add_argument('--muEnd', metavar='DECIMAL',
        type=float, default=0.2,
        help='Ending value for mu')
    parser.add_argument('--size', metavar='INTEGER',
        type=int, default=10,
        help='Size of w and b values to tune for')
    parser.add_argument('--minNodes', metavar='INTEGER',
        type=int, default=60,
        help='Minimum percentage of nodes in optimal forests\
              overlapping with terminal nodes in prize file\
              to consider as a solution')
    parser.add_argument('--processes', metavar='INTEGER',
        type=int, default=64,
        help='Number of processes to use in parallel')
    parser.add_argument('--logPath', metavar='FILE',
        default='./forest-tuner.log',
        help='Absolute path to log file')
    args = parser.parse_args()

    # setting up a logger
    logging.basicConfig(
        filename=args.logPath,
        level=logging.INFO,
        format='%(asctime)s: %(message)s',
        datefmt='%d.%m.%Y %H:%M:%S'
        )

    if not os.path.isdir(args.workingDir):
        logging.info('The working directory %s is NOT a valid directory',
            args.workingDir)
        raise SystemExit

    if not os.path.isfile(args.forestPath):
        logging.info('The forest path %s is NOT a valid file path',
            args.forestPath)
        raise SystemExit

    if not os.path.isfile(args.msgsteinerPath):
        logging.info('The msgsteiner path %s is NOT a valid file path',
            args.msgsteinerPath)
        raise SystemExit

    if not os.path.isfile(args.prizePath):
        logging.info('The prize path %s is NOT a valid file path',
            args.prizePath)
        raise SystemExit

    if not os.path.isfile(args.edgePath):
        logging.info('The edge path %s is NOT a valid file path',
            args.edgePath)
        raise SystemExit

    # get configurations based on user input
    configs = get_configs(
        {'start': args.wStart, 'end': args.wEnd},
        {'start': args.bStart, 'end': args.bEnd},
        {'start': args.muStart, 'end': args.muEnd},
        args.size)

    # directory for storing outputs
    outputs_dir = os.path.join(args.workingDir, 'outputs')
    if not os.path.exists(outputs_dir):
        os.mkdir(outputs_dir)

    # log the prize file currently worked on
    logging.info('Running forest for %s', args.prizePath)

    # list to collect jobs for running forest in parallel
    jobs = []

    # run forest for each configuration
    # obtained based on user input
    for config in configs:
        label = get_label(args.prizePath,
            config['w'], config['b'], config['mu'])
        jobs.append({
            'working_dir': args.workingDir,
            'forest_path': args.forestPath,
            'msgsteiner_path': args.msgsteinerPath,
            'prize_path': args.prizePath,
            'edge_path': args.edgePath,
            'outputs_dir': outputs_dir,
            'config': config,
            'label': label,
        })

    # limit CPU count to the machines CPU count
    # if a higher count given
    cpu_count = min(args.processes, mp.cpu_count())
    # pool of processes for parallel execution
    pool = mp.Pool(cpu_count)
    # submit jobs to worker
    results = pool.map(forest_worker, jobs)
    # close not to cause high memory use
    pool.close()
    # join to wait for collecting results
    pool.join()

    # collect the solutions under certain conditions
    solutions = get_solutions(results, args.prizePath, args.minNodes)

    # get the best solution based on number of trees
    # and average size of trees in the optimal forests
    solution = get_best_solution(solutions)

    # write the best solution to a text file
    label = get_label(args.prizePath, solution['config']['w'],
        solution['config']['b'], solution['config']['mu'])
    forest_file = make_network_file(outputs_dir, solution['F'],
        label + '_bestOptimalForest', sif = False)

    # log the final solution
    logging.info('Best config. found to be %s', ', '.join([
        k + ': ' + str(v) for k, v in solution['config'].iteritems()]))
    logging.info('Best solution written to %s', forest_file)


if __name__ == '__main__':
    main()
