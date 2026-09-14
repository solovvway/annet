Eltex ESR / MES
===============

Annet supports Eltex **ESR** service routers and **MES** switches.

The vendor is registered as ``eltex`` and matches hardware whose NetBox
manufacturer/model resolves to the ``Eltex`` devdb node (``Eltex.ESR.*`` for
routers, ``Eltex.MES.*`` for switches, ``Eltex.WEP`` for access points).

CLI model
---------

Eltex firmware presents an IOS-like hierarchical configuration:

.. code::

  esr-1# configure
  esr-1(config)# interface gigabitethernet 1/0/1
  esr-1(config-if)# description uplink
  esr-1(config-if)# switchport mode trunk
  esr-1(config-if)# exit
  esr-1(config)# exit
  esr-1# do commit
  esr-1# save

* blocks are opened by a plain row and closed with ``exit``;
* the negative form of a command is ``no <command>`` (``reverse = "no"``);
* changes are staged and applied with ``do commit``; ``save`` persists them;
* the running config is obtained with ``show running-config``.

Applying a patch
----------------

``annet deploy`` sends:

.. code::

  configure
  <patch commands>
  do commit     # when --commit is enabled
  save          # when --finalize is enabled
  exit

The commit-confirm workflow (``do commit`` followed by a timed ``do confirm``
and automatic rollback) is intentionally **not** triggered by a plain deploy:
it is an operator decision and belongs to the orchestration layer (for example
the NetOps SSH service), not to configuration generation.

Rulebooks
---------

* ``annet/rulebook/texts/eltex.rul`` — patching rules for interfaces, VLANs,
  static routes, VRF, OSPF/OSPFv3, BGP, route-maps, VRRP, MPLS/VPLS and the
  common management blocks (SNMP, NTP, AAA, LLDP, logging).
* ``annet/rulebook/texts/eltex.order`` — command ordering.
* ``annet/rulebook/texts/eltex.deploy`` — interactive ``y/N`` confirmations.

VLAN handling for ``switchport trunk allowed vlan`` and the VRF/IP-address
interaction inside interface blocks reuse the well-tested IOS logic through the
``annet.rulebook.eltex.*`` package, so Eltex never depends on Cisco internals
directly.

NetBox platform slugs
---------------------

The breed is derived from the device:

* NetBox **platform slug** equal to a known breed (``eltex``, ``ios12``,
  ``vrp55``, …) wins — use it to pin the driver explicitly;
* otherwise the manufacturer/model is mapped heuristically
  (``Eltex`` → ``eltex``).

.. code::

  # in NetBox: Manufacturer "Eltex", Device Type model "ESR-1000"
  # platform slug "eltex" is optional but recommended.

Hardware model examples and the expected devdb paths:

+-------------------+----------------------+
| HW model          | devdb path           |
+===================+======================+
| Eltex ESR-100     | Eltex.ESR.ESR100     |
+-------------------+----------------------+
| Eltex ESR-1000    | Eltex.ESR.ESR1000    |
+-------------------+----------------------+
| Eltex ESR-1511    | Eltex.ESR.ESR1511    |
+-------------------+----------------------+
| Eltex MES-2324    | Eltex.MES.MES2300    |
+-------------------+----------------------+
| Eltex MES-3300    | Eltex.MES.MES3300    |
+-------------------+----------------------+

Legacy SSH
----------

Older Eltex firmware ships an OpenSSH build that only offers ``ssh-rsa`` host
keys and SHA1 KEX algorithms.  This is a transport concern handled by the SSH
client used for ``annet diff``/``deploy`` (see the NetOps SSH service), not by
the vendor implementation in annet.
