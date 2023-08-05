import svnmock.mock as __mock
import svn.client as __client

__mock.__build_mock_api(__client, globals())
