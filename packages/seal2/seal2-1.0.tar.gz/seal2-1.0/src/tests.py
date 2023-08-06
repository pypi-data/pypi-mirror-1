import unittest
import seal2

class APITests(unittest.TestCase):
    def testModuleConstants(self):
        self.assertEqual(seal2.key_size, 20)


    def testFixedKeySize(self):
        self.assertRaises(TypeError, seal2.new)
        self.assertRaises(ValueError, seal2.new, "x")
        self.assertRaises(ValueError, seal2.new, "x"*25)
        seal2.new("x"*seal2.key_size)


    def testContextConstants(self):
        context=seal2.new("x"*seal2.key_size)
        self.assertEqual(context.key_size, 20)


class CryptTests(unittest.TestCase):

    def testBasicCrypt(self):
        # This test was taken from the Crypt::SEAL2 test
        key="\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09" \
            "\x0a\x0b\x0c\x0d\x0e\x0f\x10\x11\x12\x13"
        plaintext="\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09" \
                  "\x0a\x0b\x0c\x0d\x0e\x0f\x10\x11\x12\x13" \
                  "\x14\x15\x16\x17\x18\x19\x1a\x1b\x1c\x1d"
        ciphertext="\xd9\x8a\xcb\x4a\x47\x2b\xbc\xe0\x9c\x17" \
                   "\x10\x26\x61\xa3\x84\xf6\xbe\x30\x24\xc6" \
                   "\x25\xa1\x00\xfb\x05\xb2\xe6\xff\x46\x18"

        context=seal2.new(key)
        self.assertEqual(context.encrypt(plaintext), ciphertext)


    def testBasicDecrypt(self):
        # This test was taken from the Crypt::SEAL2 test
        key="\x00" * 20
        ciphertext="\xc3\x12\xb1\xe0\xc7\x4a\x02\x92\x89\x30" \
                   "\xe0\xa2\x71\xd3\x1a\xca\x2b\x02\x84\xa8" \
                   "\xf1\xe7\xb9\x90\xaa\xe2\x42\x56\x84\xf3"
        plaintext="\x00"*30

        context=seal2.new(key)
        self.assertEqual(context.decrypt(ciphertext), plaintext)



