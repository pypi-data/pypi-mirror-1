Sandbox environments
====================

This recipe creates a sandbox environment for deployments similar to
zc.recipe.deployment. It is not intended for system-wide installation but as a
sandboxed/development variation of the deployment pattern.

For production, system-wide deployments you can simply switch out a sandbox
deployment part with a real deployment part.

A root directory is defined for the sandbox (by default this is
`parts/${name}`) in which the following directory structure is created::

  ${root}/var/run
  ${root}/var/log
  ${root}/etc/
  ${root}/etc/cron.d
  ${root}/etc/init.d
  ${root}/etc/logrotate.d

Additionally to be able to mix multiple deployments within a single sandbox we
compute the following paths compatible to zc.recipe.deployment::

  crontab-directory
  logrotate-directory
  rc-directory
  run-directory
  log-directory
  etc-directory

Also, the `user` option is setup to match the current user.

Supported options
=================

The recipe supports a single optional option:

root
    Optional: The root directory of the sandbox. Will be computed from the
    section name if not given.


Example usage
=============

We'll start by creating a buildout that uses the recipe.

    >>> import os
    >>> write('buildout.cfg',
    ... """
    ... [buildout]
    ... parts = deployment
    ...
    ... [deployment]
    ... recipe = gocept.recipe.deploymentsandbox
    ... """)

Running the buildout gives us:

    >>> print system(buildout)
    Installing deployment.
    >>> ls(sample_buildout, 'parts')
    d deployment
    >>> ls(sample_buildout, 'parts', 'deployment')
    d etc
    d var
    >>> ls(sample_buildout, 'parts', 'deployment', 'etc')
    d  cron.d
    d  deployment
    d  init.d
    d  logrotate.d
    >>> ls(sample_buildout, 'parts', 'deployment', 'var')
    d log
    d run
    >>> ls(sample_buildout, 'parts', 'deployment', 'var', 'log')
    d deployment
    >>> ls(sample_buildout, 'parts', 'deployment', 'var', 'run')
    d deployment
