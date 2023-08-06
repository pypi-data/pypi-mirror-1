PAS Plugin to fetch groups from LDAP
====================================

Changes
=======

  * 1.1.1 (rnix - 2009-02-16)
    - set p_changed True after managing configuration. This bug was never
      detected since the LDAP Session itself was previously persisted in the
      plugin.

  * 1.1 (rnix - 2009-02-10)
    - Fix ldap property on plugin object due to changes in bda.ldap

  <= 1.1 unreleased (any)
    - initial work
