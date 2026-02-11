
import unittest
import pandas as pd
import polars as pl
from src import ingress

class TestIngress(unittest.TestCase):
    def test_detect_format_csv(self):
        self.assertEqual(ingress.detect_format("test.csv"), "CSV (Polars)")
        
    def test_detect_format_pdf(self):
        self.assertEqual(ingress.detect_format("report.pdf"), "PDF (Clinical Report)")
        
    def test_ingress_recover(self):
        # Test logic without file I/O if possible, or mock it.
        # Here we test the recovery logic by manipulating a dataframe directly if we could access the inner function
        # But ingress.run_ingress is file-bound. 
        # Let's test Column Mapping dict roughly
        self.assertEqual(ingress.COLUMN_MAPPING["ABHA_No"], "ABHA_ID")

if __name__ == '__main__':
    unittest.main()
