from Testing import ZopeTestCase

from plone.openid.plugins.oid import OpenIdPlugin
from plone.openid.tests.consumer import PatchPlugin

# Use a mock consumer for the OpenId plugin
PatchPlugin(OpenIdPlugin)

class OpenIdTestCase(ZopeTestCase.ZopeTestCase):

    identity = "http://plone.myopenid.com"
    server_response={
            "openid.mode"              : "id_res",
            "nonce"                    : "nonce",
            "openid.identity"          : "http://plone.myopenid.com",
            "openid.assoc_handle"      : "assoc_handle",
            "openid.return_to"         : "return_to",
            "openid.signed"            : "signed",
            "openid.sig"               : "sig",
            "openid.invalidate_handle" : "invalidate_handle",
            }

    _setup_fixture = False

    def afterSetUp(self):
        if self.app.hasObject("openid"):
            self.app._delObject("openid")
        self.app._setObject("openid", OpenIdPlugin("openid"))

