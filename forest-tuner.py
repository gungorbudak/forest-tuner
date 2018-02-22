import os
import csv
import argparse
import logging
import operator
import multiprocessing as mp
from csv import DictReader
from subprocess import Popen, PIPE

import numpy as np
import networkx as nx


def __range(start, stop, step):
    a = start
    yield a
    while a != stop:
        a = a + step
        yield a


def make_config_file(working_dir, config, label):
    """
    Generates the config file for the forest run

    Args:
        working_dir: Absolute path to working directory
        config: Dictionary of config parameters
        label: Unique label for the filename

    Returns:
        config_file: Absolute path to config file generated
    """
    configs_dir = os.path.join(working_dir, 'configs')
    
    # make config file if there is not one
    config_file = os.path.join(configs_dir, 'config_' + label + '.txt')
    if not os.path.isfile(config_file):
        with open(config_file, 'w') as f:
            for k, v in config.iteritems():
                f.write(k + ' = ' + str(v) + '\n')

    return config_file


def make_log_file(outputs_dir, stdout, stderr, label):
    """
    Generates log file for std output & error log from forest run

    Args:
        outputs_dir: Absolute path to outputs directory
        stdout: Standard output
        stderr: Standard error
        label: Unique label for the filename
    """
    # make logs dir if there is not one
    logs_dir = os.path.join(outputs_dir, 'logs')
    if not os.path.isdir(logs_dir):
        os.mkdir(logs_dir)

    # make log file if there is not one
    log_file = os.path.join(logs_dir, 'log_' + label + '.txt')
    with open(log_file, 'w') as f:
        if stdout:
            f.write(stdout)
        if stderr:
            f.write(stderr)

    return


def make_data_file(data, data_path):
    header = [
        'label',
        'w',
        'b',
        'mu',
        't',
        'num_prizes',
        'num_terminals',
        'num_steiners',
        'num_nodes',
        'num_edges',
        'num_trees',
        'num_singletons',
        'mean_degrees',
        'median_degrees',
        'has_ubc'
        ]

    # sorting the rows by mean Steiner degrees first
    # and then number of terminals included in the solution
    data.sort(key=operator.itemgetter('mean_degrees'))
    data.sort(key=operator.itemgetter('num_terminals'), reverse=True)

    with open(data_path, 'w') as f:
        writer = csv.DictWriter(f, fieldnames=header, delimiter='\t')
        writer.writeheader()
        for d in data:
            writer.writerow(d)

    return data_path


def get_label(prize_path, config):
    """
    Generate a label from filename of the prize file and parameter sets

    Args:
        prize_path: absolute path to the prize file
        config: dictionary of parameters

    Returns:
        label: string that consists of filename of the prize file parameters
    """
    label = ''.join([
        os.path.splitext(os.path.basename(prize_path))[0], '_',
        'w', str(config['w']),
        'b', str(config['b']),
        'mu', str(config['mu'])
        ])
    return label


def get_configs(w, b, m, processes):
    """
    Generate parameter sets from given start, end values and size

    Args:
        w: range and step size for omega parameter
        b: range and step size for beta parameter
        m: range and step size for mu parameter

    Returns:
        configs: list of parameter sets
    """
    configs = []

    ws = list(map(float, w.split(',')))
    bs = list(map(float, b.split(',')))
    ms = list(map(float, m.split(',')))
    if len(ws) == 3:
        ws = list(__range(*ws))
    if len(bs) == 3:
        bs = list(__range(*bs))
    if len(ms) == 3:
        ms = list(__range(*ms))

    for i in range(len(ws)):
        for j in range(len(bs)):
            for k in range(len(ms)):
                configs.append({
                    'w': round(ws[i], 2),
                    'b': round(bs[j], 2),
                    'mu': round(ms[k], 2),
                    'D': 10,
                    'threads': processes
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


def get_prizes(prize_path):
    nodes = set()
    with open(prize_path) as rows:
        for row in rows:
            cols = row.strip().split()
            nodes.add(cols[0])
    return nodes


def get_t(output_file):
    t = 0
    info_file = output_file.replace('_optimalForest.sif', '_info.txt')
    with open(info_file) as lines:
        for line in lines:
            line = line.strip()
            if line == '':
                break
            t = line.split()[1]
    if t != 'edges,':
        return float(t)
    return 'NA'


def get_data(results, prize_path, edge_path, min_nodes):
    # read terminal nodes from the prize file
    prizes = get_prizes(prize_path)
    prizes_size = len(prizes)

    I = get_network(edge_path, sif = False)

    data = []
    for result in results:
        F = get_network(result['forest_file'])
        # don't include forests with less than given number of edges
        if F.number_of_edges() > 0:
            # only if more than given percent of terminal nodes
            # are present in the solution
            overlap = 100 * (len(prizes.intersection(F.nodes())) /
                float(prizes_size))
            if overlap > min_nodes:
                steiner_nodes = set(F.nodes()).difference(prizes)
                n2 = len(steiner_nodes)
                n3 = F.number_of_nodes()
                n1 = n3 - n2
                n4 = F.number_of_edges()
                n5 = len([T for T in nx.connected_component_subgraphs(F)
                    if T.number_of_nodes() > 5])
                n6 = nx.number_connected_components(F) - n5
                t = get_t(result['forest_file'])
                degrees = [I.degree(node) for node in steiner_nodes]
                has_ubc = int(F.has_node('UBC'))
                data.append({
                    'label': result['label'],
                    'w': result['config']['w'],
                    'b': result['config']['b'],
                    'mu': result['config']['mu'],
                    't': t,
                    'num_prizes': prizes_size,
                    'num_terminals': n1,
                    'num_steiners': n2,
                    'num_nodes': n3,
                    'num_edges': n4,
                    'num_trees': n5,
                    'num_singletons': n6,
                    'mean_degrees': round(np.mean(degrees), 2),
                    'median_degrees': round(np.median(degrees), 2),
                    'has_ubc': has_ubc
                })

    return data


def forest_worker(job):
    working_dir = job['working_dir']
    forest_path = job['forest_path']
    msgsteiner_path = job['msgsteiner_path']
    prize_path = job['prize_path']
    edge_path = job['edge_path']
    outputs_dir = job['outputs_dir']
    config = job['config']
    label = job['label']

    config_file = make_config_file(working_dir, config, label)

    forest_file = os.path.join(outputs_dir,
        label + '_optimalForest.sif')

    if not os.path.exists(forest_file):
        command = [
            'python2', forest_path,
            '--msgpath', msgsteiner_path,
            '-p', prize_path,
            '-e', edge_path,
            '-c', config_file,
            '--outpath', outputs_dir,
            '--outlabel', label
        ]

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
            # '_optimalForest.sif',
            # '_augmentedForest.sif',
            # '_dummyForest.sif',
            # '_edgeattributes.tsv',
            # '_nodeattributes.tsv',
            # '_info.txt',
        ]

        # delete all output files except few
        for suffix in suffixes:
            output_file = os.path.join(outputs_dir, label + suffix)
            if os.path.exists(output_file):
                os.remove(output_file)

    # return the config and
    # optimal forest file obtained for data collections
    return {
        'label': label,
        'config': config,
        'forest_file': forest_file
        }


def main():
    # parsing terminal arguments
    parser = argparse.ArgumentParser(
        description='Prize-collecting Steiner Forest algorithm\
                     parameter tuner for w, b and mu parameters',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--workingDir', metavar='DIRECTORY', default='.',
        help='Working directory for configs and outputs')
    parser.add_argument('--forestPath', metavar='FILE', required=True,
        help='(required) Absolute path to forest Python script')
    parser.add_argument('--msgsteinerPath', metavar='FILE', required=True,
        help='(required) Absolute path to msgsteiner executable')
    parser.add_argument('--prizePath', metavar='FILE', required=True,
        help='(required) Absolute path to prize file')
    parser.add_argument('--edgePath', metavar='FILE', required=True,
        help='(required) Absolute path to edge file')
    parser.add_argument('-w', '--omega', metavar='START,STOP,STEP or VALUE',
        type=str, default='2.0,10.0,2.0',
        help='Range and step size for omega value')
    parser.add_argument('-b', '--beta', metavar='START,STOP,STEP or VALUE',
        type=str, default='2.0,10.0,2.0',
        help='Range and step size for beta value')
    parser.add_argument('-m', '--mu', metavar='START,STOP,STEP or VALUE',
        type=str, default='0.1',
        help='Range and step size for mu value')
    parser.add_argument('--minNodes', metavar='INTEGER',
        type=int, default=60,
        help='Minimum percentage of nodes in optimal forests\
              overlapping with terminal nodes in prize file\
              for adding the solution to data file')
    parser.add_argument('--outputsDirName', metavar='STRING',
        type=str, default='outputs',
        help='Name of the outputs directory in the given\
              working directory')
    parser.add_argument('--dataPath', metavar='FILE',
        default='./forest-tuner-data.tsv',
        help='Absolute path to data file')
    parser.add_argument('--logPath', metavar='FILE',
        default='./forest-tuner.log',
        help='Absolute path to log file')
    parser.add_argument('--processes', metavar='INTEGER',
        type=int, default=16,
        help='Number of processes to use in parallel')
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
    configs = get_configs(args.omega, args.beta, args.mu, args.processes)

    # directory for storing outputs
    outputs_dir = os.path.join(args.workingDir, args.outputsDirName)
    if not os.path.isdir(outputs_dir):
        os.mkdir(outputs_dir)

    # make the directory that will store auto-generated config files
    configs_dir = os.path.join(args.workingDir, 'configs')
    if not os.path.isdir(configs_dir):
        os.mkdir(configs_dir)

    # log the prize file currently worked on
    logging.info('Running forest for %s', args.prizePath)

    # list to collect jobs for running forest in parallel
    jobs = []

    # run forest for each configuration
    # obtained based on user input
    for config in configs:
        label = get_label(args.prizePath, config)
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

    # collect the data from all runs
    data = get_data(results, args.prizePath, args.edgePath, args.minNodes)

    # write the data
    data_path = make_data_file(data, args.dataPath)

    # log the final output
    logging.info('Tuning data written to %s', data_path)


if __name__ == '__main__':
    main()
