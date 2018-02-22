# Forest Tuner

Prize-collecting Steiner Forest (PCSF or Forest) algorithm parameter tuner for omega (w), beta (b) and mu (m) parameters. Given a range and step size or a value for every parameter, Forest Tuner runs Forest for every combination, and collects several metrics (described in Interpreation section) per run to determine the best parameters set for a particular prize set and edge set (interactome).

## Setup

Setup `OmicsIntegrator v0.3.1` and `msgsteiner v1.3` as described [in the OmicsIntegrator's repository](https://github.com/fraenkel-lab/OmicsIntegrator).

Download `forest-tuner.py` script from this repository and move it to your working directory. Use `wget` as shown below or right-click and save [this link](https://raw.githubusercontent.com/gungorbudak/forest-tuner/master/forest-tuner.py).

    wget https://raw.githubusercontent.com/gungorbudak/forest-tuner/master/forest-tuner.py

Alternatively, if you have Docker installed on your machine, you can also use the `Dockerfile` provided in this repository to setup a working Docker image/container including `Omics Integrator v0.3.1`, `msgsteiner v1.3` and `forest-tuner.py`. To do so:

    git clone https://github.com/gungorbudak/forest-tuner.git
    cd forest-tuner
    docker built -t forest-tuner:0.1 .

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

Alternatively, in the case of using a Docker container, but first make sure you have the prize and edge files in the current working directory (`$PWD`):

```
docker run -v $PWD:/data/ forest-tuner:0.1 /bin/sh -c "python /opt/forest-tuner.py --forestPath /opt/OmicsIntegrator-0.3.1/scripts/forest.py --msgsteinerPath /opt/msgsteiner-1.3/msgsteiner --prizePath /data/CT-PA_prize.tsv --edgePath /data/iref_mitab_miscore_2013_08_12_interactome.txt -w 2,10,2 -b 2,10,2 -m 0.1 --minNodes 60 --workingDir /data/ --outputsDirName outputs --processes 8"
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
* `-m` or `--mu` Range and step size or value of mu value in the forms of `start,stop,step` or `value`. Defaults to `0.1`.
* `--minNodes` Minimum percentage of nodes in optimal forests overlapping with terminal nodes in prize file for adding the solution to data file.
* `--outputsDirName` Name of the outputs directory in the given working directory.
* `--dataPath` Absolute path to output data file. Defaults to `./forest-tuner-data.tsv`.
* `--logPath` Absolute path to output log file. Defaults to `./forest-tuner.log`.
* `--processes` Number of processes to use in parallel, also used to provide `threads` config parameter to `forest.py`.

### Interpretation

The output data file contains several metrics (as columns) listed below for each parameter combination (omega, beta and mu parameters) run (as rows). The data file is sorted by `mean_degrees` in ascending order and then `num_terminals` in descencing order. The idea behind this sorting is the best solution we may search should include Steiner nodes with node high degrees and the solution includes as many terminals as possible. Other considerations can be looking for solutions without singletons and UBC as it interacts with very high number of nodes.

#### Metrics

* `t`, sum of negative prizes.
* `num_prizes`, number of prizes given to Forest Tuner.
* `num_terminals`, number of terminal nodes (prizes) recovered by Forest in the solution.
* `num_steiner`, number of Steiner nodes revealed by Forest in the solution.
* `num_nodes`, total number of nodes (terminal and Steiner) in the solution.
* `num_edges`, total number of edges in the solution.
* `num_trees`, number of connected components with node size greater than 5 in the solution.
* `num_singletons`, number of connected components with node size less than or equal to 5 in the solution.
* `num_hubs`, number of Steiner nodes in the solution with degree greater than 100.
* `mean_degrees`, mean of degrees of Steiner nodes in the solution.
* `median_degrees`, median of degrees of Steiner nodes in the solution.
* `has_ubc`, whether the solution includes UBC protein as the node.
