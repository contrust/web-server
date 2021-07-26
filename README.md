<h1 align="center">Web-server</h1>
<p>
  <img alt="Version" src="https://img.shields.io/badge/version-0.1.0-blue.svg?cacheSeconds=2592000" />
</p>

## Install

```sh
pip install .
```

## Usage

Show help

```sh
python3 -m webserver -h
```

Get config file with default values

```sh
python3 -m webserver -g output_file
```

Run server with config file

```sh
python3 -m webserver -c config_file
```

## Run tests

```sh
python3 -m unittest
```
## Features

* proxy_pass
* serve static files / directories with a cache of open files
* auto-index for catalogs
* logging requests
* virtual servers
* support for keep-alive connections
* launch of python functions to certain request paths
* configuration via config file
* multithreading


## Author

👤 **Artyom Borisov**

* Github: [@contrust](https://github.com/contrust)

