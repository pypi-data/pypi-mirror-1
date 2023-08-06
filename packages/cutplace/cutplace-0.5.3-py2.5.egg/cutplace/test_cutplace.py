"""
Tests  for cutplace application.
"""
import cutplace
import dev_test
import logging
import os.path
import parsers
import tools
import unittest

_log = logging.getLogger("cutplace")

class CutplaceTest(unittest.TestCase):
    """Test cases for cutplace command line interface."""

    def testVersion(self):
        cutPlace = cutplace.CutPlace()
        self.assertRaises(cutplace.ExitQuietlyOptionError, cutPlace.setOptions, ["--version"])
        
    def testHelp(self):
        cutPlace = cutplace.CutPlace()
        self.assertRaises(cutplace.ExitQuietlyOptionError, cutPlace.setOptions, ["--help"])
        self.assertRaises(cutplace.ExitQuietlyOptionError, cutPlace.setOptions, ["-h"])

    def testListEncodings(self):
        cutPlace = cutplace.CutPlace()
        cutPlace.setOptions(["--list-encodings"])

    # TODO: Add tests for broken CSV files.

    def testSplitValidData(self):
        icdPath = dev_test.getTestIcdPath("customers.ods")
        dataPath = dev_test.getTestInputPath("valid_customers_iso-8859-1.csv")
        cutPlace = cutplace.CutPlace()
        cutPlace.setOptions(["--split", icdPath, dataPath])
        cutPlace.validate()
        acceptedDataPath = dev_test.getTestInputPath("valid_customers_iso-8859-1_accepted.csv")
        rejectedDataPath = dev_test.getTestInputPath("valid_customers_iso-8859-1_rejected.txt")
        self.assertNotEqual(os.path.getsize(acceptedDataPath), 0)
        self.assertEqual(os.path.getsize(rejectedDataPath), 0)
        os.remove(acceptedDataPath)
        os.remove(rejectedDataPath)
        
    def testSplitBrokenData(self):
        icdPath = dev_test.getTestIcdPath("customers.ods")
        dataPath = dev_test.getTestInputPath("broken_customers.csv")
        cutPlace = cutplace.CutPlace()
        cutPlace.setOptions(["--split", icdPath, dataPath])
        cutPlace.validate()
        acceptedDataPath = dev_test.getTestInputPath("broken_customers_accepted.csv")
        rejectedDataPath = dev_test.getTestInputPath("broken_customers_rejected.txt")
        self.assertNotEqual(os.path.getsize(acceptedDataPath), 0)
        self.assertNotEqual(os.path.getsize(rejectedDataPath), 0)
        os.remove(acceptedDataPath)
        os.remove(rejectedDataPath)
        
    def _testValidIcd(self, suffix):
        assert suffix is not None
        icdPath = dev_test.getTestIcdPath("customers." + suffix)
        cutPlace = cutplace.CutPlace()
        cutPlace.setIcdFromFile(icdPath)
    
    def testValidIcdInCsvFormat(self):
        self._testValidIcd("csv")
    
    def testValidIcdInOdsFormat(self):
        self._testValidIcd("ods")
    
    def testValidIcdInXlsFormat(self):
        try:
            self._testValidIcd("xls")
        except parsers.CutplaceXlrdImportError:
            _log.warning("skipped test due lack of xlrd module")

    def testValidCsvs(self):
        VALID_PREFIX = "valid_"
        testsInputFolder = dev_test.getTestFolder("input")
        validCsvFileNames = tools.listdirMatching(testsInputFolder, VALID_PREFIX + ".*\\.csv")
        validCsvPaths = list(os.path.join(testsInputFolder, fileName) for fileName in validCsvFileNames)
        for dataPath in validCsvPaths:
            # Get file name without "valid
            baseFileName = os.path.basename(dataPath)
            baseFileNameWithoutCsvSuffix = os.path.splitext(baseFileName)[0]
            baseFileNameWithoutValidPrefixAndCsvSuffix = baseFileNameWithoutCsvSuffix[len(VALID_PREFIX):]
            icdBaseName = baseFileNameWithoutValidPrefixAndCsvSuffix.split("_")[0]
            icdFolder = os.path.join(testsInputFolder, "icds")
            icdPath = os.path.join(icdFolder, icdBaseName + ".csv")
            cutPlace = cutplace.CutPlace()
            cutPlace.setOptions([icdPath, dataPath])
            cutPlace.validate()
            # TODO: Assert number of errors detected in dataPath is 0.

    def testValidFixedTxt(self):
        icdPath = dev_test.getTestIcdPath("customers_fixed.ods")
        dataPath = dev_test.getTestInputPath("valid_customers_fixed.txt")
        cutPlace = cutplace.CutPlace()
        cutPlace.setOptions([icdPath, dataPath])
        cutPlace.validate()
        # TODO: Assert number of errors detected in dataPath is 0.
        
        
class LotsOfCustomersTest(unittest.TestCase):
    """Test case for performance profiling."""

    def testLotsOfCustomersCsv(self):
        icdOdsPath = dev_test.getTestIcdPath("customers.ods")
        locCsvPath = dev_test.getTestFile("input", "lots_of_customers.csv")
        dev_test.createLotsOfCustomersCsv(locCsvPath)
        cutPlace = cutplace.CutPlace()
        cutPlace.setOptions([icdOdsPath, locCsvPath])
        cutPlace.validate()
        # TODO: Assert number of errors detected in dataPath is 0.
        
if __name__ == '__main__': # pragma: no cover
    logging.basicConfig()
    logging.getLogger("cutplace").setLevel(logging.WARNING)
    unittest.main()
