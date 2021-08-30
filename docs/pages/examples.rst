.. _examples:

========
Examples
========

Basic Level
===========

.. raw:: html

   <div>
     <img src="../_static/basic_fire_magic.png" style="float: right; padding-left: 24px;" />
     <p>Create instance from config file with params.</p>
     <blockquote>Please note that <b>Basic Fire Magic</b> also allows your hero to cast fire spells at reduced cost.</blockquote>
   </div>

.. code-block:: yaml

   # transform.yaml
   _target_: torchvision.transforms.Normalize
   mean: [0.5, 0.5, 0.5]
   std: [0.5, 0.5, 0.5]

.. code-block:: python

   import hydra_slayer
   import yaml

   with open("transform.yaml") as stream:
       raw_config = yaml.safe_load(stream)

   transform = hydra_slayer.get_from_params(**raw_config)
   transform
   # Normalize(mean=[0.5, 0.5, 0.5], std=[0.5, 0.5, 0.5])


Advanced Level
==============

.. raw:: html

   <div>
     <img src="../_static/advanced_fire_magic.png" style="float: right; padding-left: 24px;" />
     <p>Create <a href="https://www.cs.toronto.edu/~kriz/cifar.html">CIFAR100</a> dataset from config file with params.</p>
     <blockquote>Please note that <b>Advanced Fire Magic</b> also allows your hero to cast fire spells at reduced cost and increased effectiveness.</blockquote>
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
         mean: [0.5, 0.5, 0.5]
         std: [0.5, 0.5, 0.5]
   download: true

.. code-block:: python

   import hydra_slayer
   import yaml

   with open("dataset.yaml") as stream:
       raw_config = yaml.safe_load(stream)

   dataset = hydra_slayer.get_from_params(**raw_config)
   dataset
   # Dataset CIFAR100
   #     Number of datapoints: 10000
   #     Root location: ./data
   #     Split: Test
   #     StandardTransform
   # Transform: Compose(
   #                ToTensor()
   #                Normalize(mean=[0.5, 0.5, 0.5], std=[0.5, 0.5, 0.5])
   #            )


Expert level
============

Creating ``pd.DataFrame`` from config
-------------------------------------

.. raw:: html

   <div>
     <img src="../_static/expert_fire_magic.png" style="float: right; padding-left: 24px;" />
     <p>Read multiple CSV files as pandas dataframes and merge them.</p>
     <blockquote>Please note that <b>Expert Fire Magic</b> also allows your hero to cast fire spells at reduced cost and maximum effectiveness.</blockquote>
   </div>

.. code-block:: yaml

   # dataset.yaml
   dataframe:
     _target_: pandas.merge
     left:
       _target_: pandas.read_csv
       filepath_or_buffer: dataset/dataset_part1.csv

       # By default, hydra-slayer use partial fit for functions
       # (what is useful with activation functions in neural networks).
       # But if we want to call ``pandas.read_csv`` function instead,
       # then we should pass ``call_meta_factory`` manually.
       meta_factory: &call_function
         _target_: hydra_slayer.call_meta_factory
     right:
       _target_: pandas.read_csv
       filepath_or_buffer: dataset/dataset_part2.csv
       meta_factory: *call_function
     how: inner
     'on': user
     meta_factory: *call_function

.. code-block:: python

   import hydra_slayer
   import yaml

   with open("dataset.yaml") as stream:
       raw_config = yaml.safe_load(stream)

   config = hydra_slayer.get_from_params(**raw_config)

   dataset = config["dataframe"]
   dataset
   # <class 'pandas.core.frame.DataFrame'>
   #    user country  premium  ...
   # 0     1     USA    False  ...
   # 1     2      UK     True  ...
   #     ...     ...      ...  ...


'Extending' configs
-------------------

.. raw:: html

  <div>
    <img src="../_static/expert_fire_magic.png" style="float: right; padding-left: 24px;" />
    <p>Define the dataset in a separate config file and then pass it to the main config.</p>
    <blockquote>Please note that <b>Maximum Fire Magic</b> also allows your hero to cast fire spells at reduced cost and maximum effectiveness.</blockquote>
  </div>

.. code-block:: yaml

   # dataset.yaml
   _target_: torch.utils.data.DataLoader
   dataset:
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
   batch_size: 32
   shuffle: false

.. code-block:: yaml

   # config.yaml
   dataset:
     _target_: hydra_slayer.get_from_params
     # ``yaml.safe_load`` will return dictionary with parameters,
     # but to get ``DataLoader`` additional ``hydra_slayer.get_from_params``
     # should be used.

     kwargs:
       # Read dataset from "dataset.yaml", roughly equivalent to
       #   with open("dataset.yaml") as stream:
       #       kwargs = yaml.safe_load(stream)
       _target_: yaml.safe_load
       stream:
         _target_: open
         file: dataset.yaml
       meta_factory: &call_function
         _target_: hydra_slayer.call_meta_factory

     meta_factory: *call_function

   model:
     _target_: torchvision.models.resnet18
     pretrained: true
     meta_factory:
       _target_: hydra_slayer.call_meta_factory

   criterion:
     _target_: torch.nn.CrossEntropyLoss

.. code-block:: python

   import hydra_slayer
   import torch
   import yaml

   with open("config.yaml") as stream:
       raw_config = yaml.safe_load(stream)

   config = hydra_slayer.get_from_params(**raw_config)
   model, criterion = config["model"], config["criterion"]
   model.eval()

   losses = []
   with torch.no_grad():
       for batch, labels in config["dataset"]:
           outputs = model(batch)
           loss = criterion(outputs, labels)
           losses.append(loss.tolist())
   mean_loss = sum(losses) / len(losses)
   mean_loss
   # ≈8.6087
