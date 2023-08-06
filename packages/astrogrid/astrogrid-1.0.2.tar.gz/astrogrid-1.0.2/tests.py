import unittest, md5, os, time
from astrogrid import acr
from astrogrid import ConeSearch
from astrogrid import SiapSearch
from astrogrid import Registry, Configuration
from astrogrid import MySpace

acr._config['debug'] = False

class TestACR(unittest.TestCase):
    def testLogin(self):
        self.assertEqual(acr.login(), True)
        self.assertEqual(acr.isLoggedIn(), True)
        
    #def testLogout(self):
    #    self.assertEqual(acr.logout(), True)
        
class TestCone(unittest.TestCase):
	def setUp(self):
		self.myspace = MySpace()
		self.cone = ConeSearch('ivo://ned.ipac/Basic_Data_Near_Position')
		acr._config['debug']=False
		
	def testTitle(self):
		self.assertEqual(self.cone.title, 'The NASA/IPAC Extragalactic Database')
		
	def testExecute(self):
	    res = self.cone.execute(180.0, 0.0, 0.1)
	    self.assertEqual(md5.new(res).hexdigest(), '60a406f65f730c291aae5a37676c815a')
		
	def testSaveAs(self):
		ofile = '#cone-unittest.vot'
		res = self.cone.execute(180.0, 0.0, 0.1, saveAs=ofile, clobber=True)
		res = self.myspace.readfile(res)
		self.myspace.rm(ofile)
		self.assertEqual(md5.new(res).hexdigest(), '60a406f65f730c291aae5a37676c815a')

class TestSiap(unittest.TestCase):
	def setUp(self):
		self.myspace = MySpace()
		self.siap = SiapSearch('ivo://roe.ac.uk/services/SIAPDR4-images')
		
	def testTitle(self):
		self.assertEqual(self.siap.title, 'Sloan Digital Sky Survey DR4 - Images (fixed)')
		
	def testExecute(self):
		res = self.siap.execute(180.0, 2.0, 1.0)
		self.assertEqual(md5.new(res).hexdigest(), '76f261ff258e55fabb5f069d9296f75c')

	def testSaveAs(self):
		ofile = '#siap-unittest.vot'
		res = self.siap.execute(180.0, 2.0, 1.0, saveAs=ofile, clobber=True)
		res = self.myspace.readfile(res)
		self.myspace.rm(ofile)
		self.assertEqual(md5.new(res).hexdigest(), '76f261ff258e55fabb5f069d9296f75c')
		
	def testSaveDatasets(self):
		ofile = '#siap-unittest.vot'
		res, thread = self.siap.execute(180.0, 2.0, 0.01, saveAs=ofile, saveDatasets='#unittest', clobber=True)
		while thread.isAlive():
			time.sleep(10)
			pass
		ldir = self.myspace.ls('#unittest')
		self.myspace.rm('#unittest', recursive=True)
		self.myspace.rm(res)
		self.assertEqual(len(ldir), 10)
		self.assertEqual(md5.new(','.join([f[2] for f in ldir])).hexdigest(), '89f6c08472eaa639d32fc1958dc3640b')
		
	
class TestMySpace(unittest.TestCase):
	def setUp(self):
		self.myspace = MySpace()
		self.fname = "#python-unittest.vot"
		
	def testWriteRead(self):
		res = self.myspace.savefile("1234567890", self.fname, clobber=True)
		self.assertEqual(res, True)
		res = self.myspace.readfile(self.fname)
		self.assertEqual(res, '1234567890')
		res = self.myspace.readfile(self.fname, ofile='/tmp/python-unittest.vot')
		self.assertEqual(open(res).read(), '1234567890')
		self.myspace.rm(self.fname)
		os.unlink(res)
		
	def testDelete(self):
		res = self.myspace.savefile("1234567890", self.fname, clobber=True)
		self.assertEqual(self.myspace.access(self.fname), True)
		self.myspace.rm(self.fname)
		self.assertEqual(self.myspace.access(self.fname), False)
		
class TestRegistry(unittest.TestCase):
	def setUp(self):
		self.reg = Registry()
		self.conf = Configuration()
		
	def testEndpoint(self):
		endpoint = self.reg.endpoint()
		self.assertEqual(self.reg.endpoint(), 'http://galahad.star.le.ac.uk:8080/galahad-registry/services/RegistryQuery')
		self.conf.update({'org.astrogrid.registry.query.endpoint': 'test'})
		self.assertEqual(self.reg.endpoint(), 'test')
		self.conf.update({'org.astrogrid.registry.query.endpoint': endpoint})
		self.assertEqual(self.reg.endpoint(), 'http://galahad.star.le.ac.uk:8080/galahad-registry/services/RegistryQuery')

		
if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(TestACR)
    unittest.TextTestRunner(verbosity=2).run(suite)

    suite = unittest.TestLoader().loadTestsFromTestCase(TestCone)
    unittest.TextTestRunner(verbosity=2).run(suite)

    suite = unittest.TestLoader().loadTestsFromTestCase(TestSiap)
    unittest.TextTestRunner(verbosity=2).run(suite)
    
    suite = unittest.TestLoader().loadTestsFromTestCase(TestMySpace)
    unittest.TextTestRunner(verbosity=2).run(suite)    
    
    suite = unittest.TestLoader().loadTestsFromTestCase(TestRegistry)
    unittest.TextTestRunner(verbosity=2).run(suite)        