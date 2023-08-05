import unittest
import splicetee
import os
from test import test_support

class SpliceTeeModuleTest(unittest.TestCase):
    def read_what_was_written(self, fd, buf):
        buf_tmp = ""
        while len(buf_tmp) < len(buf):
            buf_tmp += os.read(fd, len(buf) - len(buf_tmp))
        if buf_tmp != buf:
            self.fail("failed in reading what has been written"%(buf_tmp,buf))

    def test_read_write(self):
        pipe1 = os.pipe()
        buf = "splicetee"
        written = 0
        while written < len(buf):
            count = os.write(pipe1[1],buf[written:])
            written += count
        pipe2 = os.pipe()
        splicetee.tee(pipe1[0], pipe2[1], len(buf), 0)
        self.read_what_was_written(pipe2[0], buf)
        
        file = os.tmpfile()
        splicetee.splice(pipe1[0], 0, file.fileno(), 0, len(buf), 0)
        os.lseek(file.fileno(), 0, 0)
        self.read_what_was_written(file.fileno(), buf)

        file.close()
        os.close(pipe1[0])
        os.close(pipe1[1])
        os.close(pipe2[0])
        os.close(pipe2[1])
						
        

def test_main():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(SpliceTeeModuleTest))
    test_support.run_suite(suite)

if __name__ == "__main__":
    test_main()
