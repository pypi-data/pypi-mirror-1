# Copyright 2008 Neil Martinsen-Burrell
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA 


"""
Automatically update another branch and working tree on commit.

This is a Bazaar (http://bazaar-vcs.org) plugin to "mirror" the current
state of a project to another branch.  The most common use case is to
update a working tree that is on a webserver.  There is substantial
overlap between this plugin and the push-and-update plugin which updates
a working tree of a remote branch after a push to that remote branch.
(See https://launchpad.net/bzr-push-and-update for more information.)

This plugin is intended for use where the "official" version of a branch
is not on the webserver (in which case, push-and-update would work).  It
also makes the mirroring process automatic on every commit.

Installation
------------

To install the plugin, you need to put this directory under your Bazaar
plugins folder (usually ``~/.bazaar/plugins``).  An easy way to do that
is to use Bazaar to branch this project right into that directory::

  cd ~/.bazaar/plugins
  bzr branch https://launchpad.net/bzr-automirror automirror

Usage
-----

To enable mirroring, you need to add the ``post_commit_mirror``
configuration option on a branch.  See ``bzr help configuration`` about
ways this can be accomplished.  The simplest is to add
``post_commit_mirror = <URL>`` to the ``.bzr/branch/branch.conf`` file,
e.g.::

  echo "post_commit_mirror = bzr+ssh://webserver.example.com/var/htdocs/site" >> .bzr/branch/branch.conf

Multiple branches may be specified for mirroring by separating the
URLs with a comma.  If, for some reason, the URL to mirror to contains
a comma, then it must be encoded as "%44".

Current Limitations
-------------------

* Mirroring currently only works on local paths or URLs that imply ssh
  access to the remote machine (sftp://, bzr+ssh:// or svn+ssh://).

* Two separate connections are opened to the remote host.  This may mean
  entering the same password twice.
"""

from info import bzr_plugin_version as version_info

from bzrlib.branch import Branch
from bzrlib.lazy_import import lazy_import
lazy_import(globals(), """
from bzrlib.plugins.automirror.updater import Updater
""")


def branch_commit_hook(local, master,
                       old_revno, old_revid,
                       new_revno, new_revid):
    """This is the hook that will actually run after commit."""
    Updater(master, new_revid, master.get_config()).mirror_to_targets()


def branch_tip_change_hook(params):
    branch = params.branch
    new_revid = params.new_revid
    Updater(branch, new_revid, branch.get_config()).mirror_to_targets()


def install_hooks():
    """Install the hooks to run after commit."""
    if 'post_change_branch_tip' in Branch.hooks:
        Branch.hooks.install_named_hook(
            'post_change_branch_tip', branch_tip_change_hook, 'automirror')
    else:
        Branch.hooks.install_named_hook(
            'post_commit', branch_commit_hook, 'automirror')


def test_suite():
    from unittest import TestSuite
    import bzrlib.plugins.automirror.tests
    res = TestSuite()
    res.addTest(bzrlib.plugins.automirror.tests.test_suite())
    return res

install_hooks()
