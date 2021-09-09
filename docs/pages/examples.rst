.. _examples:

========
Examples
========

Basic Level
===========

Creating object from config
---------------------------

.. raw:: html

   <div>
     <img src="../_static/basic_fire_magic.png" style="float: right; padding-left: 24px; padding-bottom: 24px;" />
     <p>
       One of the ways to create instance from YAML config file is
       <code class="docutils literal notranslate"><span class="pre">get_from_params()</span></code>.
     </p>
     <blockquote>
       Please note that <b>Basic Fire Magic</b> also allows your hero to cast fire spells at reduced cost.
     </blockquote>
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


Creating objects with ``Registry``
----------------------------------

.. raw:: html

   <div>
     <img src="../_static/basic_fire_magic.png" style="float: right; padding-left: 24px; padding-bottom: 24px;" />
     <p>
       You also can add python modules to the
       <code class="docutils literal notranslate"><span class="pre">Registry()</span></code>
       and then use it to create instances by shorter (or custom) name.
     </p>
     <blockquote>
       Please note that <b>Basic Fire Magic</b> also allows your hero to cast fire spells at reduced cost.
     </blockquote>
   </div>

.. code-block:: yaml

   # transform.yaml
   _target_: Normalize
   mean: [0.5, 0.5, 0.5]
   std: [0.5, 0.5, 0.5]

.. code-block:: python

   import hydra_slayer
   import torchvision
   import yaml

   registry = hydra_slayer.Registry()
   registry.add_from_module(torchvision.transforms)
   # or you can use ``registry.add()`` to add only specific instances

   with open("transform.yaml") as stream:
       raw_config = yaml.safe_load(stream)

   transform = registry.get_from_params(**raw_config)
   transform
   # Normalize(mean=[0.5, 0.5, 0.5], std=[0.5, 0.5, 0.5])


Advanced Level
==============

Creating complex objects
------------------------

.. raw:: html

   <div>
     <img src="../_static/advanced_fire_magic.png" style="float: right; padding-left: 24px; padding-bottom: 24px;" />
     <p>
       Nested data structures can be used to create complex objects like
       <a href="https://www.cs.toronto.edu/~kriz/cifar.html">CIFAR100</a> dataset with custom transforms.
     </p>
     <blockquote>
       Please note that <b>Advanced Fire Magic</b> also allows your hero to cast fire spells at reduced cost
       and increased effectiveness.
     </blockquote>
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


Passing ``*args`` and ``**kwargs`` parameters
---------------------------------------------

.. raw:: html

   <div>
     <img src="../_static/advanced_fire_magic.png" style="float: right; padding-left: 24px; padding-bottom: 24px;" />
     <p>
       *args (<i>var-positional</i> parameter) and **kwargs (<i>var-keyword</i> parameter) parameters
       can be addressed by name, and you don't have to add
       <code class="docutils literal notranslate"><span class="pre">*</span></code> /
       <code class="docutils literal notranslate"><span class="pre">**</span></code>
       to parameter names in config.
     </p>
     <blockquote>
       Please note that <b>Advanced Fire Magic</b> also allows your hero to cast fire spells at reduced cost
       and increased effectiveness.
     </blockquote>
   </div>

.. code-block:: yaml

   # first_block.yaml
   _target_: torch.nn.Sequential
   args:
     - _target_: torch.nn.Conv2d
       in_channels: 3
       out_channels: 64
       kernel_size: 7
       stride: 2
       padding: 3
       bias: false
     - _target_: torch.nn.BatchNorm2d
       num_features: 64
     - _target_: torch.nn.ReLU
       inplace: true
     - _target_: torch.nn.MaxPool2d
       kernel_size: 3
       stride: 2
       padding: 1

.. code-block:: python

   import hydra_slayer
   import yaml

   with open("first_conv.yaml") as stream:
       raw_config = yaml.safe_load(stream)

   first_block = hydra_slayer.get_from_params(**raw_config)
   first_block
   # Sequential(
   #   (0): Conv2d(3, 64, kernel_size=(7, 7), stride=(2, 2), padding=(3, 3), bias=False)
   #   (1): BatchNorm2d(64, eps=1e-05, momentum=0.1, affine=True, track_running_stats=True)
   #   (2): ReLU(inplace=True)
   #   (3): MaxPool2d(kernel_size=3, stride=2, padding=1, dilation=1, ceil_mode=False)
   # )

.. warning::
   The order of the arguments matters in Python. If you have function like
   ``def example(arg1, *args, arg2=2, **kwargs):`` there are multiple ways to pass parameters to the function,
   for example. And in some cases *positional-or-keyword* arguments (``arg1``) can be supplied only by position.

   .. code-block:: python

      Yes:
        example(1)  # arg1=1, *args=(), arg2=2, kwargs={}
        example(1, arg2=2)  # arg1=1, *args=(,), arg2=2, kwargs={}
        example(arg1=1, arg2=4)  # arg1=1, args=(), arg2=4, kwargs={}
        example(1, 2)  # arg1=1, *args=(2,), arg2=2, kwargs={}
        example(1, 2, 3, arg2=4, arg3=5)  # arg1=1, args=(2, 3), arg2=4, kwargs={'arg3': 5}

   .. code-block:: python

      No:
        example(arg1=1, 2, 3)  # SyntaxError: positional argument follows keyword argument
        example(1, 2, arg1=3, arg2=4)  # TypeError: got multiple values for argument 'arg1'

   For the ``hydra-slayer`` the same is true. So if you want to use \*args please make sure
   that you don't specify parameters followed by \*args by keyword.


Expert level
============

Creating ``pd.DataFrame`` from config
-------------------------------------

.. raw:: html

   <div>
     <img src="../_static/expert_fire_magic.png" style="float: right; padding-left: 24px; padding-bottom: 24px;" />
     <p>You also can read multiple CSV files as pandas dataframes and merge them.</p>
     <blockquote>
       Please note that <b>Expert Fire Magic</b> also allows your hero to cast fire spells at reduced cost
       and maximum effectiveness.
     </blockquote>
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


Extending configs
-----------------

.. raw:: html

  <div>
    <img src="../_static/expert_fire_magic.png" style="float: right; padding-left: 24px; padding-bottom: 24px;" />
    <p>It is also possible define the dataset in a separate config file and then pass it to the main config.</p>
    <blockquote>
      Please note that <b>Maximum Fire Magic</b> also allows your hero to cast fire spells at reduced cost
      and maximum effectiveness.
    </blockquote>
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
