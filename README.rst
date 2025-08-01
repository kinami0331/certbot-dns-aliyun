Aliyun DNS Authenticator plugin for Certbot
===========================================

Installation
------------

.. code-block:: bash

   pip install git+https://github.com/kinami0331/certbot-dns-aliyun

Credentials
-----------
.. code-block:: ini

    dns_aliyun_access_key_id = <your access key>
    dns_aliyun_access_key_secret = <your access key secret>

Usage
-----

.. code-block:: bash

   certbot certonly \
      --authenticator dns-aliyun \
      --dns-aliyun-credentials '/path/to/credentials.ini' \
      -d '*.example.com'
