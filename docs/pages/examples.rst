.. _examples:

========
Examples
========

Basic Level
^^^^^^^^^^^

.. raw:: html

   <div>
     <img src="../_static/basic_fire_magic.png" style="float: right; padding-left: 24px;" />
     <p>Create <a href="https://www.cs.toronto.edu/~kriz/cifar.html">CIFAR100</a> dataset from config file with params.</p>
     <blockquote>Please note that <b>Basic Fire Magic</b> also allows your hero to cast fire spells at reduced cost.</blockquote>
   </div>

.. code-block:: yaml

   # dataset.yaml
   _target_: torchvision.datasets.CIFAR100
   root: ./data
   train: false
   transform:
     _target_: torchvision.transforms.Compose
     transforms:
       - _target_: torchvision.transforms.ToTensor
       - _target_: torchvision.transforms.Normalize
         mean: [0.1307]
         std: [0.3081]
   download: true

.. code-block:: python

   import hydra_slayer
   import yaml

   registry = hydra_slayer.Registry()
   with open("dataset.yaml") as stream:
       config = yaml.safe_load(stream)

   dataset = registry.get_from_params(**config)
   dataset
   # Dataset CIFAR100
   #     Number of datapoints: 10000
   #     Root location: ./data
   #     Split: Test
   #     StandardTransform
   # Transform: Compose(
   #     ToTensor()
   #     Normalize(mean=[0.5, 0.5, 0.5], std=[0.5, 0.5, 0.5])
   # )


Advanced Level
^^^^^^^^^^^^^^

.. raw:: html

   <div>
     <img src="../_static/advanced_fire_magic.png" style="float: right; padding-left: 24px;" />
     <p>Read multiple CSV files as pandas dataframes and merge them.</p>
     <blockquote>Please note that <b>Advanced Fire Magic</b> also allows your hero to cast fire spells at reduced cost and increased effectiveness.</blockquote>
   </div>

.. code-block:: yaml

   # dataset.yaml
   dataframe:
     _target_: pandas.merge
     left:
       _target_: pandas.read_csv
       filepath_or_buffer: dataset/dataset_part1.csv
     right:
       _target_: pandas.read_csv
       filepath_or_buffer: dataset/dataset_part2.csv
     how: inner
     on: user

     # TODO: add comments why we need meta factory
     meta_factory:
       _target_: catalyst.tools.registry.call_meta_factory

.. code-block:: python

   import hydra_slayer
   import yaml

   registry = hydra_slayer.Registry()
   with open("config.yaml") as stream:
       raw_config = yaml.safe_load(stream)

   config = registry.get_from_params(**raw_config)

   dataset = config["dataframe"]
   dataset
   # <pandas.core.frame.DataFrame>...

Expert level
^^^^^^^^^^^^

.. raw:: html

  <div>
    <img src="../_static/expert_fire_magic.png" style="float: right; padding-left: 24px;" />
    <p>Sorry, the person who is responsible for the expert level example was eaten by hydras last week.</p>
    <blockquote>Please note that <b>Expert Fire Magic</b> also allows your hero to cast fire spells at reduced cost and maximum effectiveness.</blockquote>
  </div>

..
  .. code-block:: yaml

    # dataset.yaml
    _target_: torchvision.datasets.CIFAR100
    root: ./data
    train: false
    transform:
      _target_: torchvision.transforms.Compose
      transforms:
        - _target_: torchvision.transforms.ToTensor
        - _target_: torchvision.transforms.Normalize
          mean: [0.5,0.5,0.5]
          std: [0.5,0.5,0.5]
    download: true

  .. code-block:: yaml

    # config.yaml
    dataset:
      _target_: torch.utils.data.DataLoader
      # TODO: will not work as dict will be retuned, not dataset
      dataset:
        # read dataset from "dataset.yaml",
        # roughly equivalent to
        # with open("dataset.yaml") as stream:
        #     params = yaml.safe_load(stream)
        _target_: yaml.safe_load
        stream:
          _target_: open
          file: dataset_config.yaml
        meta_factory:
          _target_: hydra_slayer.call_meta_factory
      batch_size: 32
      shuffle: false

    model:
      _target_: torchvision.models.resnet18
      pretrained: true
      meta_factory:
        _target_: hydra_slayer.call_meta_factory

  .. code-block:: python

    import hydra_slayer
    import torch
    import yaml

    registry = hydra_slayer.Registry()
    with open("config.yaml") as stream:
        raw_config = yaml.safe_load(stream)

    config = registry.get_from_params(**raw_config)
    model, dataset = config["model"], config["dataset"]

    model.eval()
    with torch.no_grad():
        for batch, y_true in dataset:
            y_preds = model(batch)
