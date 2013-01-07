qrpickle
--------

Serializes numpy arrays by creating a sequence of QR codes that could be
printed and scanned to recreate the original array.  It currently has plenty
of bugs and short-comings.

I don't recommend using this, but it is a fun hack.

Depdendencies
~~~~~~~~~~~~~
numpy
PIL
zbar
pypdf
qrcode (https://github.com/lincolnloop/python-qrcode)

TODO
~~~~
Drop PIL and qrcode dependency.

Licence
~~~~~~~
WTFPL as appropriate.  Depends on numpy (BSD), PIL (BSD), zbar (LGPLv2.1),
pypdf (BSD), qrcode (BSD).
