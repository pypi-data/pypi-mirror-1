from plone.openid.tests.oitestcase import FunctionalOpenIdTestCase
from zExceptions import Redirect


class TestOpenIdAuthentication(FunctionalOpenIdTestCase):

    def buildServerResponse(self):
        credentials={}
        for field in [ "nonce", "openid.assoc_handle", "openid.return_to",
                        "openid.signed", "openid.sig",
                        "openid.invalidate_handle", "openid.mode"]:
            credentials[field]=field
        credentials["openid.identity"]=self.identity
        credentials["openid.source"]="server"

        return credentials


    def testEmptyAuthentication(self):
        """Test if we do not invent an identity out of thin air.
        """
        creds=self.app.folder.openid.authenticateCredentials({})
        self.assertEqual(creds, None)


    def testUnknownOpenIdSource(self):
        """Test if an incorrect source does not produce unexpected exceptions.
        """
        creds=self.app.folder.openid.authenticateCredentials({"openid.source" : "x"})
        self.assertEqual(creds, None)


    def testServerAuthentication(self):
        """Test authentication of OpenID server responses.
        """
        credentials=self.buildServerResponse()
        creds=self.app.folder.openid.authenticateCredentials(credentials)
        self.assertEqual(creds, (self.identity, self.identity))


    def testIncompleteServerAuthentication(self):
        """Test authentication of OpenID server responses.
        """
        credentials=self.buildServerResponse()
        del credentials["openid.sig"]
        creds=self.app.folder.openid.authenticateCredentials(credentials)
        self.assertEqual(creds, None)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite=TestSuite()
    suite.addTest(makeSuite(TestOpenIdAuthentication))
    return suite
