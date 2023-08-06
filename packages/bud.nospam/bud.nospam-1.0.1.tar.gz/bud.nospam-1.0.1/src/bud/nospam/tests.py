import unittest
import bud.nospam

class TestNoSpam(unittest.TestCase):

    def test_rot13_encryption(self):
        self.failUnless(
            bud.nospam.rot_13_encrypt('bugga') == 'ohttn',
            'Simple encryption'
        )
        self.failUnless(
            bud.nospam.rot_13_encrypt('someguy@someaddress.comma') == \
            'fbzrthl\\100fbzrnqqerff\\056pbzzn',
            'Email-like encryption'
        )
        self.failUnless(
            bud.nospam.rot_13_encrypt('tricky \/ \n multi-line ... @ encrypt \n -!abcdefghijklmnopqrstuvwxyz') == \
            'gevpxl \\\\057 \n zhygv-yvar \\056\\056\\056 \\100 rapelcg \n -!nopqrstuvwxyzabcdefghijklm',
            'Tricky multi-line encryption'
        )

    def test_js_obfuscated_text(self):
        self.failUnless(
            bud.nospam.js_obfuscated_text('emailaddy@example.com') == \
            '<script type="text/javascript">document.write(\n"rznvynqql\\100rknzcyr\\056pbz".replace(/[a-zA-Z]/g, function(c){return String.fromCharCode((c<="Z"?90:122)>=(c=c.charCodeAt(0)+13)?c:c-26);})\n);\n</script>',
            'Encrypted email with Javascript protection'
        )
        
    def test_js_obfuscated_mailto(self):
        self.failUnless(
            bud.nospam.js_obfuscated_text('emailaddy@example.com') == \
            '<script type="text/javascript">document.write(\n"rznvynqql\\100rknzcyr\\056pbz".replace(/[a-zA-Z]/g, function(c){return String.fromCharCode((c<="Z"?90:122)>=(c=c.charCodeAt(0)+13)?c:c-26);})\n);\n</script>',
            'Mailto encrypted email'
        )
        self.failUnless(
            bud.nospam.js_obfuscated_mailto('emailadd@example.com','Email Addy') == \
            '<script type="text/javascript">document.write(\n"<n uers=\\"znvygb:rznvynqq\\100rknzcyr\\056pbz\\">Rznvy Nqql<\\057n>".replace(/[a-zA-Z]/g, function(c){return String.fromCharCode((c<="Z"?90:122)>=(c=c.charCodeAt(0)+13)?c:c-26);})\n);\n</script>',
            'Mailto encrypted email with name'
        )

def test_suite():
    return unittest.TestLoader().loadTestsFromTestCase(TestNoSpam)
