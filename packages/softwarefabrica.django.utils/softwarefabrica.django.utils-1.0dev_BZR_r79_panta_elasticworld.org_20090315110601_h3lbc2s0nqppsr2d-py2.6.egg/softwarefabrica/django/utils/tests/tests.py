# -*- coding: utf-8 -*-
r"""
>>> import os
>>> from django import forms
>>> from softwarefabrica.django.utils.IPv4MaskedAddressField import *
>>> from softwarefabrica.django.utils.tests.models import *

>>> neruda = Author(name = 'Pablo', last_name = 'Neruda', birth_year = 1904, active = True)
>>> neruda.save()

>>> shakespeare = Author(name = 'William', last_name = 'Shakespeare', birth_year = 1564, active = True)
>>> shakespeare.save()

>>> book = Book(title = "A Midsummer Night's Dream", isbn='ABCD12', author=shakespeare, active=True)
>>> book.save()

>>> f = IPv4MaskedAddressFormField()
>>> f.clean('')
Traceback (most recent call last):
...
ValidationError: [u'This field is required.']
>>> f.clean(None)
Traceback (most recent call last):
...
ValidationError: [u'This field is required.']

>>> f.clean('127.0.0.1/24')
u'127.0.0.1/24'

>>> f.clean('127.0.0.1/32')
u'127.0.0.1/32'

>>> f.clean('127.0.0.1/255.255.255.0')
u'127.0.0.1/255.255.255.0'

>>> f.clean('127.0.0.1')
u'127.0.0.1'

>>> f.clean('foo')
Traceback (most recent call last):
...
ValidationError: [u'Enter a valid IPv4 (masked) address.']
>>> f.clean('127.0.0.')
Traceback (most recent call last):
...
ValidationError: [u'Enter a valid IPv4 (masked) address.']
>>> f.clean('1.2.3.4.5')
Traceback (most recent call last):
...
ValidationError: [u'Enter a valid IPv4 (masked) address.']
>>> f.clean('256.125.1.5')
Traceback (most recent call last):
...
ValidationError: [u'Enter a valid IPv4 (masked) address.']

>>> f.clean('1.1.0.1/22')
u'1.1.0.1/22'

>>> f.clean('1.2.3.4/27')
u'1.2.3.4/27'

>>> f.clean('1.2.3.4/37')
Traceback (most recent call last):
...
ValidationError: [u'Enter a valid IPv4 (masked) address.']

>>> f = IPv4MaskedAddressFormField(required=False)
>>> f.clean('')
u''
>>> f.clean(None)
u''
>>> f.clean('127.0.0.1')
u'127.0.0.1'
>>> f.clean('foo')
Traceback (most recent call last):
...
ValidationError: [u'Enter a valid IPv4 (masked) address.']

>>> f.clean('127.0.0.')
Traceback (most recent call last):
...
ValidationError: [u'Enter a valid IPv4 (masked) address.']
>>> f.clean('1.2.3.4.5')
Traceback (most recent call last):
...
ValidationError: [u'Enter a valid IPv4 (masked) address.']
>>> f.clean('256.125.1.5')
Traceback (most recent call last):
...
ValidationError: [u'Enter a valid IPv4 (masked) address.']

>>> data = IPAddressData(ip = '192.168.1.1')
>>> data.save()

>>> print data
192.168.1.1/32

>>> data.ip
IPv4('192.168.1.1/32')

>>> data.ip.ip
3232235777L

>>> data.ip.ip_ext
'192.168.1.1'

>>> data.ip.ip_ext_full
'192.168.1.1'

>>> data.ip.network
3232235777L

>>> data.ip.network_ext
'192.168.1.1'

>>> data.ip.hostmask
0L

>>> data.ip.hostmask_ext
'0.0.0.0'

>>> data.ip.broadcast
3232235777L

>>> data.ip.broadcast_ext
'192.168.1.1'

>>> data.ip.netmask
4294967295L

>>> data.ip.netmask_ext
'255.255.255.255'

>>> data.ip.prefixlen
32

>>> data = IPAddressData(ip = '192.168.1.1/37')
Traceback (most recent call last):
...
IPv4NetmaskValidationError: '37' is not a valid IPv4 netmask

>>> data = IPAddressData(ip = '192.168.1.23/24')
>>> data.save()

>>> print data
192.168.1.23/24

>>> data.ip
IPv4('192.168.1.23/24')

>>> data.ip.ip
3232235799L

>>> data.ip.ip_ext
'192.168.1.23'

>>> data.ip.ip_ext_full
'192.168.1.23'

>>> data.ip.network
3232235776L

>>> data.ip.network_ext
'192.168.1.0'

>>> data.ip.hostmask
255L

>>> data.ip.hostmask_ext
'0.0.0.255'

>>> data.ip.broadcast
3232236031L

>>> data.ip.broadcast_ext
'192.168.1.255'

>>> data.ip.netmask
4294967040L

>>> data.ip.netmask_ext
'255.255.255.0'

>>> data.ip.prefixlen
24

"""
