# forest-tuner

Prize-collecting Steiner Forest (PCSF or forest) algorithm parameter tuner for w and b parameters

## Setup

Setup `msgsteiner 1.1` and `OmicsIntegrator 0.2.0` as described [in the OmicsIntegrator's repository](https://github.com/fraenkel-lab/OmicsIntegrator).

Download `forest-tuner.py` script from this repository and move to your working directory.

## Run

### Getting help

    usage: forest-tuner.py [-h] [--workingDir WORKINGDIR] --forestPath FORESTPATH
                       --msgsteinerPath MSGSTEINERPATH --prizePath PRIZEPATH
                       --edgePath EDGEPATH [--wStart WSTART] [--wEnd WEND]
                       [--bStart BSTART] [--bEnd BEND] [--size SIZE]

    Prize-collecting Steiner Forest algorithm parameter tuner for w and b
    parameters

    optional arguments:
    -h, --help            show this help message and exit
    --workingDir WORKINGDIR
                        Working directory for configs, logs and outputs
                        (default: .)
    --forestPath FORESTPATH
                        Absolute path to forest Python script (default: None)
    --msgsteinerPath MSGSTEINERPATH
                        Absolute path to msgsteiner executable (default: None)
    --prizePath PRIZEPATH
                        Absolute path to prize file (default: None)
    --edgePath EDGEPATH   Absolute path to edge file (default: None)
    --wStart WSTART       Starting value for w (default: 1.0)
    --wEnd WEND           Ending value for w (default: 10.0)
    --bStart BSTART       Starting value for b (default: 1.0)
    --bEnd BEND           Ending value for b (default: 10.0)
    --size SIZE           Size of w and b values to tune for (default: 10)

### Example

    python forest-tuner.py --workingDir /home/gungor/projects/cptac --forestPath /home/gungor/softwares/OmicsIntegrator-0.2.0/scripts/forest.py --msgsteinerPath /home/gungor/softwares/msgsteiner-1.1/msgsteiner --edgePath /home/gungor/projects/cptac/PSICQUIC_UPDATED_05162013.txt --prizePath /home/gungor/projects/cptac/prizes/ovarian_S1T5.txt --wStart 1.0 --wEnd 10.0 --bStart 1.0 --bEnd 10.0 --size 10
