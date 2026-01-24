from app import db
from datetime import datetime
from enum import Enum


class WeighingStatus(Enum):
    """Status enum for weighing transaction workflow"""
    WAITING_GROSS = "waiting_gross"
    SORTING = "sorting"
    WAITING_TARE = "waiting_tare"
    COMPLETED = "completed"


class DONumber(db.Model):
    """Delivery Order Number model"""
    __tablename__ = 'do_numbers'
    
    id = db.Column(db.Integer, primary_key=True)
    do_number = db.Column(db.String(50), unique=True, nullable=False, index=True)
    supplier_name = db.Column(db.String(100))
    vehicle_number = db.Column(db.String(20))
    driver_name = db.Column(db.String(100))
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    weighing_transactions = db.relationship('WeighingTransaction', backref='do', lazy=True)
    
    def __repr__(self):
        return f'<DONumber {self.do_number}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'do_number': self.do_number,
            'supplier_name': self.supplier_name,
            'vehicle_number': self.vehicle_number,
            'driver_name': self.driver_name,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class WeighingTransaction(db.Model):
    """Weighing transaction model tracking the complete workflow"""
    __tablename__ = 'weighing_transactions'
    
    id = db.Column(db.Integer, primary_key=True)
    do_number_id = db.Column(db.Integer, db.ForeignKey('do_numbers.id'), nullable=False)
    
    # Status tracking
    status = db.Column(db.String(20), nullable=False, default=WeighingStatus.WAITING_GROSS.value)
    
    # Weight measurements
    gross_weight = db.Column(db.Float)  # Bruto
    gross_time = db.Column(db.DateTime)  # Jam masuk
    tare_weight = db.Column(db.Float)  # Tarra
    tare_time = db.Column(db.DateTime)  # Jam keluar
    net_weight = db.Column(db.Float)  # Netto (gross - tare)
    
    # Deductions
    total_deduction = db.Column(db.Float, default=0.0)  # Potongan
    net_after_deduction = db.Column(db.Float)  # Netto akhir
    
    # Audit trail
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.String(100))
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    updated_by = db.Column(db.String(100))
    
    # Relationships
    deductions = db.relationship('Deduction', backref='transaction', lazy=True, cascade='all, delete-orphan')
    audit_logs = db.relationship('AuditLog', backref='transaction', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<WeighingTransaction {self.id} - {self.status}>'
    
    def calculate_weights(self):
        """Calculate net weight and net after deduction"""
        if self.gross_weight is not None and self.tare_weight is not None:
            self.net_weight = self.gross_weight - self.tare_weight
            self.net_after_deduction = self.net_weight - (self.total_deduction or 0.0)
    
    def to_dict(self):
        return {
            'id': self.id,
            'do_number_id': self.do_number_id,
            'do_number': self.do.do_number if self.do else None,
            'status': self.status,
            'gross_weight': self.gross_weight,
            'gross_time': self.gross_time.isoformat() if self.gross_time else None,
            'tare_weight': self.tare_weight,
            'tare_time': self.tare_time.isoformat() if self.tare_time else None,
            'net_weight': self.net_weight,
            'total_deduction': self.total_deduction,
            'net_after_deduction': self.net_after_deduction,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'created_by': self.created_by,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'updated_by': self.updated_by
        }


class Deduction(db.Model):
    """Deduction/Potongan model for sorting phase"""
    __tablename__ = 'deductions'
    
    id = db.Column(db.Integer, primary_key=True)
    transaction_id = db.Column(db.Integer, db.ForeignKey('weighing_transactions.id'), nullable=False)
    
    # Deduction details
    deduction_type = db.Column(db.String(50))  # e.g., 'damaged', 'unripe', 'overripe'
    amount = db.Column(db.Float, nullable=False)
    remarks = db.Column(db.Text)
    
    # Timestamps
    sorting_time = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.String(100))
    
    def __repr__(self):
        return f'<Deduction {self.id} - {self.deduction_type}: {self.amount}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'transaction_id': self.transaction_id,
            'deduction_type': self.deduction_type,
            'amount': self.amount,
            'remarks': self.remarks,
            'sorting_time': self.sorting_time.isoformat() if self.sorting_time else None,
            'created_by': self.created_by
        }


class AuditLog(db.Model):
    """Audit log for tracking status changes and modifications"""
    __tablename__ = 'audit_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    transaction_id = db.Column(db.Integer, db.ForeignKey('weighing_transactions.id'), nullable=False)
    
    # Audit details
    action = db.Column(db.String(50), nullable=False)  # e.g., 'status_change', 'weight_recorded'
    old_value = db.Column(db.Text)
    new_value = db.Column(db.Text)
    description = db.Column(db.Text)
    
    # Tracking
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.String(100))
    
    def __repr__(self):
        return f'<AuditLog {self.id} - {self.action}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'transaction_id': self.transaction_id,
            'action': self.action,
            'old_value': self.old_value,
            'new_value': self.new_value,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'created_by': self.created_by
        }
