import svnmock.mock as __mock
import svn.delta as __delta

__mock.__build_mock_api(__delta, globals())
