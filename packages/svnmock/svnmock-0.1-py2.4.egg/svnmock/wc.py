import svnmock.mock as __mock
import svn.wc as __wc

__mock.__build_mock_api(__wc, globals())
