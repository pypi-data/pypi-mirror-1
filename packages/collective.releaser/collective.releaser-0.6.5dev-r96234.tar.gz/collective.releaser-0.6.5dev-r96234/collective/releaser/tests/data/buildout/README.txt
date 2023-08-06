===================
myproject buildouts
===================
buildout collection for myproject. To run them, launch the bootstrap script
with the right `cfg` file:

- `deploy`: will create a zeo server with one node, for deployement
- `dev`: will create a development server

The default buildout is `development` and will be used if no option
is provided.

steps:

1. check the xxx.cfg file for options

2. run this commands:

    python2.4 bootstrap.py -c xxx.cfg
    bin/buildout -c xxx.cfg

That's all !

