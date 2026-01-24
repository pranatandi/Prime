"""
Unit tests for the Palm Fruit Weighing System.
Tests models, calculations, and workflow logic.
"""
import unittest
from datetime import datetime

from app import app, db
from app.models import DONumber, WeighingTransaction, Deduction, WeighingStatus


class TestModels(unittest.TestCase):
    """Test database models"""
    
    def setUp(self):
        """Set up test database"""
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app = app.test_client()
        
        with app.app_context():
            db.create_all()
    
    def tearDown(self):
        """Clean up test database"""
        with app.app_context():
            db.session.remove()
            db.drop_all()
    
    def test_create_do_number(self):
        """Test creating a DO number"""
        with app.app_context():
            do = DONumber(
                do_number='TEST-001',
                supplier_name='Test Supplier',
                vehicle_number='B1234XYZ'
            )
            db.session.add(do)
            db.session.commit()
            
            retrieved = DONumber.query.filter_by(do_number='TEST-001').first()
            self.assertIsNotNone(retrieved)
            self.assertEqual(retrieved.supplier_name, 'Test Supplier')
            self.assertTrue(retrieved.is_active)
    
    def test_weighing_transaction_workflow(self):
        """Test complete weighing transaction workflow"""
        with app.app_context():
            # Create DO Number
            do = DONumber(do_number='TEST-002')
            db.session.add(do)
            db.session.commit()
            
            # Create transaction
            txn = WeighingTransaction(
                do_number_id=do.id,
                status=WeighingStatus.WAITING_GROSS.value
            )
            db.session.add(txn)
            db.session.commit()
            
            # Verify initial state
            self.assertEqual(txn.status, 'waiting_gross')
            self.assertIsNone(txn.gross_weight)
            
            # Record gross weight
            txn.gross_weight = 25000.0
            txn.gross_time = datetime.utcnow()
            txn.status = WeighingStatus.SORTING.value
            db.session.commit()
            
            self.assertEqual(txn.status, 'sorting')
            self.assertEqual(txn.gross_weight, 25000.0)
    
    def test_deduction_calculation(self):
        """Test deduction calculations"""
        with app.app_context():
            # Create DO and transaction
            do = DONumber(do_number='TEST-003')
            db.session.add(do)
            db.session.commit()
            
            txn = WeighingTransaction(
                do_number_id=do.id,
                status=WeighingStatus.SORTING.value,
                gross_weight=25000.0
            )
            db.session.add(txn)
            db.session.commit()
            
            # Add deductions
            deduction1 = Deduction(
                transaction_id=txn.id,
                deduction_type='damaged',
                amount=100.0
            )
            deduction2 = Deduction(
                transaction_id=txn.id,
                deduction_type='unripe',
                amount=50.0
            )
            db.session.add(deduction1)
            db.session.add(deduction2)
            
            txn.total_deduction = 150.0
            db.session.commit()
            
            self.assertEqual(txn.total_deduction, 150.0)
            self.assertEqual(len(txn.deductions), 2)
    
    def test_weight_calculations(self):
        """Test net weight and final weight calculations"""
        with app.app_context():
            # Create DO and transaction
            do = DONumber(do_number='TEST-004')
            db.session.add(do)
            db.session.commit()
            
            txn = WeighingTransaction(
                do_number_id=do.id,
                gross_weight=25000.0,
                tare_weight=8000.0,
                total_deduction=200.0
            )
            db.session.add(txn)
            
            # Calculate weights
            txn.calculate_weights()
            db.session.commit()
            
            # Verify calculations
            # net_weight = gross - tare = 25000 - 8000 = 17000
            self.assertEqual(txn.net_weight, 17000.0)
            
            # net_after_deduction = net - deduction = 17000 - 200 = 16800
            self.assertEqual(txn.net_after_deduction, 16800.0)
    
    def test_invalid_tare_weight(self):
        """Test that tare weight cannot exceed gross weight"""
        with app.app_context():
            # Create DO and transaction
            do = DONumber(do_number='TEST-005')
            db.session.add(do)
            db.session.commit()
            
            txn = WeighingTransaction(
                do_number_id=do.id,
                gross_weight=8000.0,
                tare_weight=10000.0  # Invalid: tare > gross
            )
            db.session.add(txn)
            
            # Should raise ValueError
            with self.assertRaises(ValueError) as context:
                txn.calculate_weights()
            
            self.assertIn('cannot be greater than', str(context.exception))


class TestAPI(unittest.TestCase):
    """Test API endpoints"""
    
    def setUp(self):
        """Set up test client"""
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app = app.test_client()
        
        with app.app_context():
            db.create_all()
    
    def tearDown(self):
        """Clean up"""
        with app.app_context():
            db.session.remove()
            db.drop_all()
    
    def test_create_do_number_api(self):
        """Test DO number creation via API"""
        response = self.app.post('/api/do-numbers',
            json={
                'do_number': 'API-TEST-001',
                'supplier_name': 'Test Supplier'
            }
        )
        
        self.assertEqual(response.status_code, 201)
        data = response.get_json()
        self.assertEqual(data['do_number'], 'API-TEST-001')
    
    def test_scan_do_number_api(self):
        """Test DO number scanning/enqueuing via API"""
        # First create a DO number
        self.app.post('/api/do-numbers',
            json={'do_number': 'API-TEST-002'}
        )
        
        # Then scan it
        response = self.app.post('/api/scan',
            json={
                'do_number': 'API-TEST-002',
                'operator': 'Test Operator'
            }
        )
        
        self.assertEqual(response.status_code, 201)
        data = response.get_json()
        self.assertTrue(data['success'])
        self.assertEqual(data['transaction']['status'], 'waiting_gross')
    
    def test_invalid_do_number_scan(self):
        """Test scanning non-existent DO number"""
        response = self.app.post('/api/scan',
            json={'do_number': 'NON-EXISTENT'}
        )
        
        self.assertEqual(response.status_code, 404)
        data = response.get_json()
        self.assertIn('error', data)


if __name__ == '__main__':
    unittest.main()
