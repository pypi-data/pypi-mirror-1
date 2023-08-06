import re
import string

rot_13_trans = string.maketrans(
    'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz',
    'NOPQRSTUVWXYZABCDEFGHIJKLMnopqrstuvwxyzabcdefghijklm'
)

def rot_13_encrypt(line):
    """Rotate 13 encryption"""
    line = line.translate(rot_13_trans)
    line = re.sub('(?=[\\"])', r'\\', line)
    line = re.sub('\n', r'\n', line)
    line = re.sub('@', r'\\100', line)
    line = re.sub('\.', r'\\056', line)
    line = re.sub('/', r'\\057', line)
    return line

def js_obfuscated_text(text):
    "ROT 13 encryption with embedded in Javascript code to decrypt in the browser."
    return """<script type="text/javascript">document.write(
"%s".replace(/[a-zA-Z]/g, function(c){return String.fromCharCode((c<="Z"?90:122)>=(c=c.charCodeAt(0)+13)?c:c-26);})
);
</script>""" % rot_13_encrypt(text)

def js_obfuscated_mailto(email, displayname=None):
    "ROT 13 encryption within an Anchor tag w/ a mailto: attribute"
    if not displayname:
        displayname = email
    return js_obfuscated_text("""<a href="mailto:%s">%s</a>""" % (
        email, displayname
    ))
