import unittest
import directio
import os
import resource
from test import test_support

class DirectioModuleTest(unittest.TestCase):
    def read_what_was_written(self, fd, buf):
        buf_tmp = ""
        while len(buf_tmp) < len(buf):
            buf_tmp += directio.read(fd, len(buf) - len(buf_tmp))
        if buf_tmp != buf:
            self.fail("failed in reading what has been written"%(buf_tmp,buf))

    def test_read_write(self):
		    flags = directio.O_RDWR | directio.O_CREAT
        fd = directio.open("tmp_directio_file", flags, 0644)
        buf = "a"*resource.getpagesize()
        sent = 0
        while sent < len(buf):
            count = directio.write(fd, buf[sent:])
            sent += count
        os.lseek(fd, 0, 0)
        self.read_what_was_written(fd, buf)
        directio.close(fd)
        os.unlink("tmp_directio_file")
						
        

def test_main():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(DirectioModuleTest))
    test_support.run_suite(suite)

if __name__ == "__main__":
    test_main()
