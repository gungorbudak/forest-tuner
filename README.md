# forest-tuner

Prize-collecting Steiner Forest (PCSF or forest) algorithm parameter tuner for w and b parameters

## Setup

Setup `msgsteiner 1.1` and `OmicsIntegrator 0.2.0` as described [in the OmicsIntegrator's repository](https://github.com/fraenkel-lab/OmicsIntegrator).

Download `forest-tuner.py` script from this repository and move to your working directory. Use `wget` as shown below or right-click and save [this link](https://raw.githubusercontent.com/gungorbudak/forest-tuner/master/forest-tuner.py).

    wget https://raw.githubusercontent.com/gungorbudak/forest-tuner/master/forest-tuner.py

## Run

### Example

    python forest-tuner.py --workingDir /home/gungor/projects/cptac --forestPath /home/gungor/softwares/OmicsIntegrator-0.2.0/scripts/forest.py --msgsteinerPath /home/gungor/softwares/msgsteiner-1.1/msgsteiner --edgePath /home/gungor/projects/cptac/PSICQUIC_UPDATED_05162013.txt --prizePath /home/gungor/projects/cptac/prizes/ovarian_S1T60.txt --wStart 1.0 --wEnd 10.0 --bStart 1.0 --bEnd 10.0 --size 10


### Getting help

    usage: forest-tuner.py [-h] [--workingDir DIR] --forestPath FILE
                           --msgsteinerPath FILE --prizePath FILE --edgePath FILE
                           [--wStart DECIMAL] [--wEnd DECIMAL] [--bStart DECIMAL]
                           [--bEnd DECIMAL] [--size INTEGER] [--minNodes INTEGER]

    Prize-collecting Steiner Forest algorithm parameter tuner for w and b
    parameters

    optional arguments:
      -h, --help            show this help message and exit
      --workingDir DIR      Working directory for configs and outputs (default: .)
      --forestPath FILE     (required) Absolute path to forest Python script
                            (default: None)
      --msgsteinerPath FILE
                            (required) Absolute path to msgsteiner executable
                            (default: None)
      --prizePath FILE      (required) Absolute path to prize file (default: None)
      --edgePath FILE       (required) Absolute path to edge file (default: None)
      --wStart DECIMAL      Starting value for w (default: 1.0)
      --wEnd DECIMAL        Ending value for w (default: 10.0)
      --bStart DECIMAL      Starting value for b (default: 1.0)
      --bEnd DECIMAL        Ending value for b (default: 10.0)
      --size INTEGER        Size of w and b values to tune for (default: 10)
      --minNodes INTEGER    Minimum percentage of nodes in optimal forests
                            overlapping with terminal nodes in prize file to
                            consider as a solution (default: 60)
