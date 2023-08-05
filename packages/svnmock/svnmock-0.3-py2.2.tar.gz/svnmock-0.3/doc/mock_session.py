# Module controlling mock data
from svnmock import mock

# Modules containing mocked-up SVN API
from svnmock import core, repo, fs

### Create and populate a new session
#####################################
ses = mock.MockSession()

# If no return value is specified to Command (3rd param),
# it will create a new object() instance and return that,
# both from ses.add() and whenever core.svn_pool_create is called.
#
# It is intended that the return value from Command (which gets
# passed through ses.add()) can be used
# to track objects from call to call; for example, in the second line
# here, it would be an error to pass anything to svn_pool_create except
# for the pool returned by the first call to svn_pool_create
pool = ses.add_command(core.svn_pool_create, [None])
scratch_pool = ses.add_command(core.svn_pool_create, [pool])

repo = ses.add_command(repos.svn_repos_open, ['/path/to/repo', pool])
fs = ses.add_command(repos.svn_repos_fs, [repo])
ses.add_command(fs.youngest_rev, [fs, pool], 8)


### If you want to have a particular command raise an error, you can
####################################################################
ses.add_error(fs.revision_root, [fs, 9, pool], TypeError)
ses.add_error(fs.revision_root, [fs, 10, pool], TypeError("Give up already"))


### If you don't care what order certain commands are run in, use the
### any_order method
#####################################################################
command_1 = Command(fs.revision_root, [fs, 19, pool])
command_2 = Command(fs.revision_root, [fs, 20, pool])

# any_order, unlike add_command, does not provide a usable return value
ses.any_order([command_1, command_2])


### In order to group commands given to the any_order method, the
### Seq (short for "Sequence") wrapper may be used:
###
### Note: we use Command() instances here, but Error() instances
### may be used as well
#################################################################
def mock_check_history(rev_root, path, rev):
    com_1 = Command(fs.node_history, [rev_root, path, rev])
    com_2 = Command(fs.history_prev, [com_1.return_val, 0, self.pool])
    com_3 = Command(fs.history_location, [com_1.return_val, self.pool], 10)
    return [com_1, com_2, com_3]

# Note that the .return_val attribute of the Seq instance
# will be equal to the return_val attribute of the final command in
# the sequence      
seq_1 = Seq(mock_check_history(my_root, 'foo/bar.py', 3))
seq_2 = Seq(mock_check_history(my_root, 'bar/foo.py', 3))

ses.any_order([seq_1, seq_2])


### Up till now, the session object is not hooked up to the API functions
### in svnmock.{mock,fs,repos,...}; to do this, associate the session
### with the module.
###
### In this case, this step is unnecessary; by default, the first session
### created is automatically assigned to mock.active_session
#########################################################################
mock.active_session = ses


### Switching sessions works just like a normal assignment-swap
###############################################################
first_ses = mock.active_session
mock.active_session = second_ses


### Deactivating the mock module entirely is done by assigning None to
### mock.active_session
######################################################################
mock.active_session = None
