<img src="https://raw.githubusercontent.com/catalyst-team/hydra-slayer/master/docs/_static/slayer.png" width="198" align="right">

# Hydra Slayer

[![build](https://github.com/catalyst-team/hydra-slayer/actions/workflows/build.yml/badge.svg)](https://github.com/catalyst-team/hydra-slayer/actions/workflows/build.yml)
[![Pipi version](https://img.shields.io/pypi/v/hydra-slayer)](https://pypi.org/project/hydra-slayer/)
[![Python Version](https://img.shields.io/pypi/pyversions/hydra-slayer)](https://pypi.org/project/hydra-slayer/)
[![License](https://img.shields.io/github/license/catalyst-team/hydra-slayer)](LICENSE)
[![Slack](https://img.shields.io/badge/slack-join_chat-brightgreen.svg)](https://join.slack.com/t/catalyst-team-core/shared_invite/zt-d9miirnn-z86oKDzFMKlMG4fgFdZafw)

**Hydra Slayer** is a 4th level spell in the School of Fire Magic.
Depending of the level of expertise in fire magic,
slayer spell increases attack of target troop by 8 against
behemoths, dragons, hydras, and other creatures.

What is more, it also allows configuring of complex applications just by config and few lines of code.

---

## Installation
Using pip you can easily install the latest release version [PyPI](https://pypi.org/):

```sh
pip install hydra-slayer
```

## Example
```yaml title="dataset.yaml"
dataset:
  _target_: torchvision.datasets.CIFAR100
  root: ./data
  train: false
  download: true
```

```python title="run.py"
import hydra_slayer
import yaml

with open("dataset.yaml") as stream:
    raw_config = yaml.safe_load(stream)

config = hydra_slayer.get_from_params(**raw_config)
config["dataset"]
# Dataset CIFAR100
#     Number of datapoints: 10000
#     Root location: ./data
#     Split: Test
```

Please check [documentation](https://catalyst-team.github.io/hydra-slayer/master/pages/examples) for more examples.

## Documentation
Full documentation for the project is available at https://catalyst-team.github.io/hydra-slayer

## Communication
- GitHub Issues: Bug reports, feature requests, install issues, RFCs, thoughts, etc.
- Slack: The [Catalyst Slack](https://join.slack.com/t/catalyst-team-core/shared_invite/zt-d9miirnn-z86oKDzFMKlMG4fgFdZafw) hosts a primary audience of moderate to experienced Hydra-Slayer (and Catalyst) users and developers for general chat, online discussions, collaboration, etc.
- Email: Feel free to use [feedback@catalyst-team.com](mailto:feedback@catalyst-team.com) as an additional channel for feedback.

## Citation
Please use this bibtex if you want to cite this repository in your publications:

    @misc{catalyst,
        author = {Sergey Kolesnikov and Yauheni Kachan},
        title = {Hydra-Slayer},
        year = {2021},
        publisher = {GitHub},
        journal = {GitHub repository},
        howpublished = {\url{https://github.com/catalyst-team/hydra-slayer}},
    }
