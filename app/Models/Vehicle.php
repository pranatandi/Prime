<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Factories\HasFactory;
use App\Traits\Auditable;

class Vehicle extends Model
{
    use HasFactory, Auditable;

    protected $fillable = [
        'plate_number',
        'type',
        'driver_name',
        'driver_phone',
        'status',
    ];

    public function weighingTransactions()
    {
        return $this->hasMany(Weighing::class);
    }
}
