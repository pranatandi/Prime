<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Factories\HasFactory;
use App\Traits\Auditable;

class Weighing extends Model
{
    use HasFactory, Auditable;

    protected $table = 'weighing_transactions';

    protected $fillable = [
        'transaction_code',
        'supplier_id',
        'vehicle_id',
        'vehicle_plate_number',
        'gross_weight',
        'tare_weight',
        'net_weight',
        'weighing_datetime',
        'vehicle_photo',
        'notes',
        'user_id',
    ];

    protected $casts = [
        'weighing_datetime' => 'datetime',
        'gross_weight' => 'decimal:2',
        'tare_weight' => 'decimal:2',
        'net_weight' => 'decimal:2',
    ];

    public function supplier()
    {
        return $this->belongsTo(Supplier::class);
    }

    public function vehicle()
    {
        return $this->belongsTo(Vehicle::class);
    }

    public function user()
    {
        return $this->belongsTo(User::class);
    }

    public function getWeighingTimeAttribute()
    {
        return $this->weighing_datetime;
    }
}
