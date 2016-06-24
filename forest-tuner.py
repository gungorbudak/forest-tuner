import os
import argparse
import numpy as np
from csv import DictReader
from subprocess import Popen, PIPE


def get_label(prize_file, w, b):
    label = ''.join([
        os.path.splitext(os.path.basename(prize_file))[0], '_',
        'W', str(w).replace('.', ''),
        'B', str(b).replace('.', '')])
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


def make_log_file(working_dir, stdin, stdout, label):
    logs_dir = os.path.join(working_dir, 'logs')
    if not os.path.exists(logs_dir):
        os.mkdir(logs_dir)
    log_file = os.path.join(logs_dir, 'log_' + label + '.txt')
    with open(log_file, 'w') as f:
        if stdin:
            f.write(stdin)
        if stdout:
            f.write(stdout)
    return


def run_forest_run(working_dir, forest_path, msgsteiner_path,
        prizes_file, edges_file, config_file, label):
    outputs_dir = os.path.join(working_dir, 'outputs')
    if not os.path.exists(outputs_dir):
        os.mkdir(outputs_dir)
    # create a command for running forest
    command = [
        'python',
        forest_path,
        '--msgpath',
        msgsteiner_path,
        '-p',
        prizes_file,
        '-e',
        edges_file,
        '-c',
        config_file,
        '--outpath',
        outputs_dir,
        '--outlabel',
        label
    ]

    # run the command
    process = Popen(
        command,
        stdin=PIPE,
        stdout=PIPE,
        )
    stdin, stdout = process.communicate()

    # write output and errors to a log file
    make_log_file(working_dir, stdin, stdout, label)

    # delete all output files except optimal forest
    os.remove(os.path.join(outputs_dir, label + '_augmentedForest.sif'))
    os.remove(os.path.join(outputs_dir, label + '_dummyForest.sif'))
    os.remove(os.path.join(outputs_dir, label + '_edgeattributes.tsv'))
    os.remove(os.path.join(outputs_dir, label + '_nodeattributes.tsv'))
    os.remove(os.path.join(outputs_dir, label + '_info.txt'))

    # return the optimal forest obtained for testing
    return os.path.join(outputs_dir, label + '_optimalForest.sif')


def main():
    # parsing terminal arguments
    parser = argparse.ArgumentParser(
        description='Prize-collecting Steiner Forest algorithm\
                     parameter tuner for w and b parameters',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--workingDir', default='.',
        help='Working directory for configs, logs and outputs')
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
    # get configurations based on user input
    configs = get_configs(
                {'start': args.wStart, 'end': args.wEnd},
                {'start': args.bStart, 'end': args.bEnd},
                args.size)
    print 'Running forest for', args.prizePath
    # run forest for each configuration obtained based on user input
    for config in configs:
        print ', '.join([k + ': ' + str(v) for k, v in config.iteritems()])
        label = get_label(args.prizePath, config['w'], config['b'])
        config_file = make_config_file(args.workingDir, config, label)
        optimal_forest = run_forest_run(args.workingDir, args.forestPath,
                            args.msgsteinerPath, args.prizePath, args.edgePath,
                            config_file, label)

if __name__ == '__main__':
    main()
