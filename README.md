# forest-tuner

Prize-collecting Steiner Forest (PCSF or forest) algorithm parameter tuner for w, b and mu parameters. Given intervals for each parameter and size which sets the number of values to be taken from the intervals, forest tuner runs PCSF for every combination, and determines the best solution among all optimal solution by finding the minimum difference between number of trees in an optimal forest and average size of trees in the optimal forest.

## Setup

Setup `msgsteiner 1.3` and `OmicsIntegrator 0.3.1` as described [in the OmicsIntegrator's repository](https://github.com/fraenkel-lab/OmicsIntegrator).

Download `forest-tuner.py` script from this repository and move to your working directory. Use `wget` as shown below or right-click and save [this link](https://raw.githubusercontent.com/gungorbudak/forest-tuner/master/forest-tuner.py).

    wget https://raw.githubusercontent.com/gungorbudak/forest-tuner/master/forest-tuner.py

## Run

### Example

```
python forest-tuner.py \
--forestPath /home/gungor/softwares/OmicsIntegrator-0.3.1/scripts/forest.py \
--msgsteinerPath /home/gungor/softwares/msgsteiner-1.3/msgsteiner \
--prizePath ./CT-PA_prize.tsv \
--edgePath ./iref_mitab_miscore_2013_08_12_interactome.txt \
-w 2,10,2 -b 2,10,2 -m 0.1 \
--minNodes 60 --outputsDirName outputs --processes 8
```

### Usage

```
python forest-tuner.py [arguments]
```

#### Arguments

* `--forestPath` (required) Absolute path to forest.py script in Omics Integrator installation.
* `--msgsteinerPath` (required) Absolute path to msgsteiner executable in msgsteiner installation.
* `--prizePath` (required) Absolute path to tab-separated values of terminals and their prizes.
* `--edgePath` (required) Absolute path to interactome.
* `-w` or `--omega` Range and step size or value of omega value in the forms of `start,stop,step` or `value`. Defaults to `2.0,10.0,2.0`.
* `-b` or `--beta` Range and step size or value of beta value in the forms of `start,stop,step` or `value`. Defaults to `2.0,10.0,2.0`.
* `-m` or `--mu` Range and step size or value of mu value in the forms of `start,stop,step` or `value`. Defaults to `0.1`
* `--minNodes` Minimum percentage of nodes in optimal forests overlapping with terminal nodes in prize file for adding the solution to data file.
* `--outputsDirName` Name of the outputs directory in the given working directory.
* `--dataPath` Absolute path to output data file. Defaults to `./forest-tuner-data.tsv`.
* `--logPath` Absolute path to output log file. Defaults to `./forest-tuner.log`.
* `--processes` Number of processes to use in parallel, also used to provide `threads` config parameter to `forest.py`.
