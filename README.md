<h1 align="center">
  FourCIPP 🐍
</h1>

FourCIPP (**FourC** **I**nput **P**ython **P**arser) holds a Python Parser to simply interact with [4C](https://www.4c-multiphysics.org/) YAML input files. This tool provides a streamlined approach to data handling for third party tools.

FourCIPP utilizes the `4C_metadata.yaml` file to ensure that projects remain up-to-date and consistent with the latest features. FourCIPP aims to enhance the efficiency of 4C data processing while promoting the use of YAML in project workflows.

## Overview <!-- omit from toc -->
- [Installation](#installation)
- [Developing FourCIPP](#developing-fourcipp)
- [Dependency Management](#dependency-management)
- [License](#license)



## Installation

For a quick and easy start an Anaconda/Miniconda environment is highly recommended. Other ways to install FourCIPP are possible but here the installation procedure is explained based on a conda install. After installing Anaconda/Miniconda
execute the following steps:

- Create a new Anaconda environment:
```bash
conda create -n fourcipp python=3.12
```

- Activate your newly created environment:
```bash
conda activate fourcipp
```

- Install all requirements with:
```
pip install .
```

Now you are up and running 🎉

## Developing FourCIPP

If you plan on actively developing FourCIPP it is advisable to install in editable mode with the development requirements like

```bash
pip install -e .[dev]
```

You can install the pre-commit hook with:
```
pre-commit install
```

## Dependency Management

To ease the dependency update process [`pip-tools`](https://github.com/jazzband/pip-tools) is utilized. To create the necessary [`requirements.txt`](./requirements.txt) file simply execute

```
pip-compile --all-extras --output-file=requirements.txt requirements.in
````

To upgrade the dependencies simply execute

```
pip-compile --all-extras --output-file=requirements.txt --upgrade requirements.in
````

## License

This project is licensed under a MIT license. For further information check [`LICENSE`](./LICENSE).
