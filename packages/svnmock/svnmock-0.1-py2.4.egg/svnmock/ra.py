import svnmock.mock as __mock
import svn.ra as __ra

__mock.__build_mock_api(__ra, globals())
