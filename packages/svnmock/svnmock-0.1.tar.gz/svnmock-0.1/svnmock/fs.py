import svnmock.mock as __mock
import svn.fs as __fs

__mock.__build_mock_api(__fs, globals())
