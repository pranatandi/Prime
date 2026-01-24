"""
Flask routes for the palm fruit weighing system.
Implements the complete workflow from DO scanning to slip generation.
"""
from flask import render_template, request, jsonify, redirect, url_for
from app import app, db
from app.models import DONumber, WeighingTransaction, Deduction, AuditLog, WeighingStatus
from app.scale_reader import read_scale_weight, ScaleReader
from datetime import datetime


def add_audit_log(transaction_id, action, old_value, new_value, description, user):
    """Helper function to add audit log entries"""
    audit = AuditLog(
        transaction_id=transaction_id,
        action=action,
        old_value=str(old_value) if old_value else None,
        new_value=str(new_value) if new_value else None,
        description=description,
        created_by=user
    )
    db.session.add(audit)


@app.route('/')
def index():
    """Home page with navigation"""
    return render_template('index.html')


@app.route('/scan')
def scan_page():
    """QR/Barcode scan page"""
    return render_template('scan.html')


@app.route('/queue')
def queue_page():
    """Operator queue screen"""
    # Get all active transactions
    transactions = WeighingTransaction.query.order_by(WeighingTransaction.created_at.desc()).all()
    return render_template('queue.html', transactions=transactions)


@app.route('/sorting/<int:transaction_id>')
def sorting_page(transaction_id):
    """Sorting input screen"""
    transaction = WeighingTransaction.query.get_or_404(transaction_id)
    return render_template('sorting.html', transaction=transaction)


@app.route('/slip/<int:transaction_id>')
def slip_page(transaction_id):
    """Weighing slip view/print page"""
    transaction = WeighingTransaction.query.get_or_404(transaction_id)
    return render_template('slip.html', transaction=transaction)


# API Endpoints

@app.route('/api/do-numbers', methods=['GET'])
def get_do_numbers():
    """Get all DO numbers"""
    do_numbers = DONumber.query.filter_by(is_active=True).all()
    return jsonify([do.to_dict() for do in do_numbers])


@app.route('/api/do-numbers', methods=['POST'])
def create_do_number():
    """Create a new DO number (for admin/setup)"""
    data = request.get_json()
    
    # Check if DO number already exists
    existing = DONumber.query.filter_by(do_number=data['do_number']).first()
    if existing:
        return jsonify({'error': 'DO number already exists'}), 400
    
    do = DONumber(
        do_number=data['do_number'],
        supplier_name=data.get('supplier_name'),
        vehicle_number=data.get('vehicle_number'),
        driver_name=data.get('driver_name')
    )
    
    db.session.add(do)
    db.session.commit()
    
    return jsonify(do.to_dict()), 201


@app.route('/api/scan', methods=['POST'])
def scan_do_number():
    """
    Scan QR/Barcode for DO Number and enqueue vehicle.
    Creates a new weighing transaction with status 'waiting_gross'.
    """
    data = request.get_json()
    do_number = data.get('do_number', '').strip()
    
    if not do_number:
        return jsonify({'error': 'DO number is required'}), 400
    
    # Validate DO number exists and is active
    do = DONumber.query.filter_by(do_number=do_number, is_active=True).first()
    
    if not do:
        return jsonify({'error': 'DO number not found or inactive'}), 404
    
    # Create new weighing transaction
    transaction = WeighingTransaction(
        do_number_id=do.id,
        status=WeighingStatus.WAITING_GROSS.value,
        created_by=data.get('operator', 'system')
    )
    
    db.session.add(transaction)
    db.session.commit()
    
    # Add audit log
    add_audit_log(
        transaction.id,
        'enqueue',
        None,
        WeighingStatus.WAITING_GROSS.value,
        f'Vehicle enqueued for DO {do_number}',
        data.get('operator', 'system')
    )
    db.session.commit()
    
    return jsonify({
        'success': True,
        'transaction': transaction.to_dict(),
        'message': 'Vehicle successfully enqueued'
    }), 201


@app.route('/api/transactions/<int:transaction_id>/gross-weight', methods=['POST'])
def record_gross_weight(transaction_id):
    """
    Record gross weight (bruto) from scale indicator.
    Reads weight automatically via USB/Serial.
    """
    transaction = WeighingTransaction.query.get_or_404(transaction_id)
    data = request.get_json() or {}
    
    # Validate status
    if transaction.status != WeighingStatus.WAITING_GROSS.value:
        return jsonify({'error': f'Invalid status. Expected waiting_gross, got {transaction.status}'}), 400
    
    try:
        # Read weight from scale
        weight = read_scale_weight()
        
        # Update transaction
        old_status = transaction.status
        transaction.gross_weight = weight
        transaction.gross_time = datetime.utcnow()
        transaction.status = WeighingStatus.SORTING.value
        transaction.updated_by = data.get('operator', 'system')
        
        # Add audit log
        add_audit_log(
            transaction.id,
            'gross_weight_recorded',
            None,
            weight,
            f'Gross weight recorded: {weight} kg',
            data.get('operator', 'system')
        )
        
        add_audit_log(
            transaction.id,
            'status_change',
            old_status,
            transaction.status,
            f'Status changed from {old_status} to {transaction.status}',
            data.get('operator', 'system')
        )
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'transaction': transaction.to_dict(),
            'weight': weight,
            'message': f'Gross weight recorded: {weight} kg'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to read weight: {str(e)}'}), 500


@app.route('/api/transactions/<int:transaction_id>/deductions', methods=['POST'])
def add_deduction(transaction_id):
    """
    Add deduction/potongan during sorting phase.
    Multiple deductions can be added for the same transaction.
    """
    transaction = WeighingTransaction.query.get_or_404(transaction_id)
    data = request.get_json()
    
    # Validate status
    if transaction.status != WeighingStatus.SORTING.value:
        return jsonify({'error': f'Invalid status. Expected sorting, got {transaction.status}'}), 400
    
    # Create deduction
    deduction = Deduction(
        transaction_id=transaction.id,
        deduction_type=data.get('deduction_type'),
        amount=float(data.get('amount', 0)),
        remarks=data.get('remarks'),
        created_by=data.get('operator', 'system')
    )
    
    db.session.add(deduction)
    
    # Update total deduction
    transaction.total_deduction = (transaction.total_deduction or 0) + deduction.amount
    transaction.updated_by = data.get('operator', 'system')
    
    # Add audit log
    add_audit_log(
        transaction.id,
        'deduction_added',
        None,
        deduction.amount,
        f'Deduction added: {deduction.deduction_type} - {deduction.amount} kg',
        data.get('operator', 'system')
    )
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'deduction': deduction.to_dict(),
        'total_deduction': transaction.total_deduction,
        'message': 'Deduction added successfully'
    }), 201


@app.route('/api/transactions/<int:transaction_id>/complete-sorting', methods=['POST'])
def complete_sorting(transaction_id):
    """
    Complete sorting phase and move to waiting_tare status.
    """
    transaction = WeighingTransaction.query.get_or_404(transaction_id)
    data = request.get_json() or {}
    
    # Validate status
    if transaction.status != WeighingStatus.SORTING.value:
        return jsonify({'error': f'Invalid status. Expected sorting, got {transaction.status}'}), 400
    
    # Update status
    old_status = transaction.status
    transaction.status = WeighingStatus.WAITING_TARE.value
    transaction.updated_by = data.get('operator', 'system')
    
    # Add audit log
    add_audit_log(
        transaction.id,
        'status_change',
        old_status,
        transaction.status,
        f'Sorting completed. Total deductions: {transaction.total_deduction} kg',
        data.get('operator', 'system')
    )
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'transaction': transaction.to_dict(),
        'message': 'Sorting completed. Ready for tare weighing.'
    })


@app.route('/api/transactions/<int:transaction_id>/tare-weight', methods=['POST'])
def record_tare_weight(transaction_id):
    """
    Record tare weight (tarra) from scale indicator.
    Reads weight automatically via USB/Serial.
    Calculates net weight and final weight after deductions.
    Updates status to completed.
    """
    transaction = WeighingTransaction.query.get_or_404(transaction_id)
    data = request.get_json() or {}
    
    # Validate status
    if transaction.status != WeighingStatus.WAITING_TARE.value:
        return jsonify({'error': f'Invalid status. Expected waiting_tare, got {transaction.status}'}), 400
    
    try:
        # Read weight from scale
        weight = read_scale_weight()
        
        # Update transaction
        old_status = transaction.status
        transaction.tare_weight = weight
        transaction.tare_time = datetime.utcnow()
        transaction.status = WeighingStatus.COMPLETED.value
        transaction.updated_by = data.get('operator', 'system')
        
        # Calculate weights
        transaction.calculate_weights()
        
        # Add audit log
        add_audit_log(
            transaction.id,
            'tare_weight_recorded',
            None,
            weight,
            f'Tare weight recorded: {weight} kg',
            data.get('operator', 'system')
        )
        
        add_audit_log(
            transaction.id,
            'weights_calculated',
            None,
            {
                'net_weight': transaction.net_weight,
                'net_after_deduction': transaction.net_after_deduction
            },
            f'Net: {transaction.net_weight} kg, Final: {transaction.net_after_deduction} kg',
            data.get('operator', 'system')
        )
        
        add_audit_log(
            transaction.id,
            'status_change',
            old_status,
            transaction.status,
            f'Transaction completed',
            data.get('operator', 'system')
        )
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'transaction': transaction.to_dict(),
            'weight': weight,
            'net_weight': transaction.net_weight,
            'net_after_deduction': transaction.net_after_deduction,
            'message': f'Tare weight recorded. Transaction completed.'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to read weight: {str(e)}'}), 500


@app.route('/api/transactions/<int:transaction_id>', methods=['GET'])
def get_transaction(transaction_id):
    """Get transaction details with all related data"""
    transaction = WeighingTransaction.query.get_or_404(transaction_id)
    
    result = transaction.to_dict()
    result['deductions'] = [d.to_dict() for d in transaction.deductions]
    result['audit_logs'] = [a.to_dict() for a in transaction.audit_logs]
    result['do_details'] = transaction.do.to_dict() if transaction.do else None
    
    return jsonify(result)


@app.route('/api/transactions', methods=['GET'])
def get_transactions():
    """Get all transactions with optional status filter"""
    status = request.args.get('status')
    
    query = WeighingTransaction.query
    if status:
        query = query.filter_by(status=status)
    
    transactions = query.order_by(WeighingTransaction.created_at.desc()).all()
    
    return jsonify([t.to_dict() for t in transactions])


@app.route('/api/scale/test', methods=['GET'])
def test_scale():
    """Test scale connection and read a sample weight"""
    try:
        reader = ScaleReader()
        success, weight = reader.test_connection()
        
        if success:
            return jsonify({
                'success': True,
                'weight': weight,
                'mock_mode': reader.mock_mode,
                'message': 'Scale connection successful'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Scale connection failed'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Scale test failed'
        }), 500
