<h1 align="center">dotctl</h1>

<p align="center"> cross-system customization using dot files
    <br>
</p>

<div align="center">

[![Status](https://img.shields.io/badge/status-active-success.svg)]()
[![GitHub Issues](https://img.shields.io/github/issues/wwmoraes/dotctl.svg)](https://github.com/wwmoraes/dotctl/issues)
[![GitHub Pull Requests](https://img.shields.io/github/issues-pr/wwmoraes/dotctl.svg)](https://github.com/wwmoraes/dotctl/pulls)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](/LICENSE)

<!-- [![Docker Image Size (latest semver)](https://img.shields.io/docker/image-size/wwmoraes/dotctl)](https://hub.docker.com/r/wwmoraes/dotctl) -->
<!-- [![Docker Image Version (latest semver)](https://img.shields.io/docker/v/wwmoraes/dotctl?label=image%20version)](https://hub.docker.com/r/wwmoraes/dotctl) -->
<!-- [![Docker Pulls](https://img.shields.io/docker/pulls/wwmoraes/dotctl)](https://hub.docker.com/r/wwmoraes/dotctl) -->

[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=wwmoraes_dotctl&metric=alert_status)](https://sonarcloud.io/dashboard?id=wwmoraes_dotctl)
[![Reliability Rating](https://sonarcloud.io/api/project_badges/measure?project=wwmoraes_dotctl&metric=reliability_rating)](https://sonarcloud.io/dashboard?id=wwmoraes_dotctl)
[![Bugs](https://sonarcloud.io/api/project_badges/measure?project=wwmoraes_dotctl&metric=bugs)](https://sonarcloud.io/dashboard?id=wwmoraes_dotctl)
[![Security Rating](https://sonarcloud.io/api/project_badges/measure?project=wwmoraes_dotctl&metric=security_rating)](https://sonarcloud.io/dashboard?id=wwmoraes_dotctl)
[![Vulnerabilities](https://sonarcloud.io/api/project_badges/measure?project=wwmoraes_dotctl&metric=vulnerabilities)](https://sonarcloud.io/dashboard?id=wwmoraes_dotctl)

[![Maintainability Rating](https://sonarcloud.io/api/project_badges/measure?project=wwmoraes_dotctl&metric=sqale_rating)](https://sonarcloud.io/dashboard?id=wwmoraes_dotctl)
[![Coverage](https://sonarcloud.io/api/project_badges/measure?project=wwmoraes_dotctl&metric=coverage)](https://sonarcloud.io/dashboard?id=wwmoraes_dotctl)
[![Code Smells](https://sonarcloud.io/api/project_badges/measure?project=wwmoraes_dotctl&metric=code_smells)](https://sonarcloud.io/dashboard?id=wwmoraes_dotctl)
[![Technical Debt](https://sonarcloud.io/api/project_badges/measure?project=wwmoraes_dotctl&metric=sqale_index)](https://sonarcloud.io/dashboard?id=wwmoraes_dotctl)

</div>

---

> DISCLAIMER: this is a WIP and is not yet released officially. Use at your own
> risk 😄

## 📝 Table of Contents

- [About](#about)
- [Getting Started](#getting_started)
- [Deployment](#deployment)
- [Usage](#usage)
- [Built Using](#built_using)
- [Contributing](../CONTRIBUTING.md)
- [Authors](#authors)
- [Acknowledgments](#acknowledgement)

## 🧐 About <a name = "about"></a>

dotctl simplifies the management of customization files, a.k.a. "dotfiles", and
packages/applications on multiple hosts. It provides tools to ease the task of
setting up and maintaining your hosts configured.

## 🏁 Getting Started <a name = "getting_started"></a>

You can install from pypi using a python package manager such as pip:

```shell
pip install dotctl
```

It is also possible to install directly from a copy of this repository:

```shell
git clone https://github.com/wwmoraes/dotctl
cd dotctl
python setup.py install
```

### Prerequisites

- Python 3.9+
- GNU stow binary on path
- `sudo` binary on path
- a user with `su` permissions

## 🔧 Running the tests <a name = "tests"></a>

All tests can be run using pipenv scripts:

- `test`: unit/integration/functional tests using `pytest`
- `sast`: SAST validations using `bandit`
- `issues`: checks for potential type problems using `mypy`
- `imports`: checks for unused imports using `pyflakes`

## 🎈 Usage <a name="usage"></a>

After install you'll have available these commands:

- dotctl
- dotfiles
- dotsecrets
- dotrun

TODO refactor and explain commands prior to v1 release

## 🚀 Deployment <a name = "deployment"></a>

TODO instructions on how to configure a dotfiles repository and use dotctl.

## ⛏️ Built Using <a name = "built_using"></a>

- [Python](https://www.python.org) - base language
- [Click](https://palletsprojects.com/p/click/) - awesome CLI kit
- [GNU Stow](https://www.gnu.org/software/stow/) - **the** symlink farm manager
- [sudo project](https://github.com/sudo-project/sudo) - to get [sandwiches](https://xkcd.com/149/) done

## ✍️ Authors <a name = "authors"></a>

- [@wwmoraes](https://github.com/wwmoraes) - Idea & Initial work

## 🎉 Acknowledgements <a name = "acknowledgement"></a>

- Hat tip to anyone whose code was used
- Inspiration
- References
