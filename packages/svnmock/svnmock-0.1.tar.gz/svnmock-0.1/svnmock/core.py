import svnmock.mock as __mock
import svn.core as __core

__mock.__build_mock_api(__core, globals())
