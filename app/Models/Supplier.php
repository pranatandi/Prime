<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Factories\HasFactory;
use App\Traits\Auditable;

class Supplier extends Model
{
    use HasFactory, Auditable;

    protected $fillable = [
        'name',
        'code',
        'phone',
        'address',
        'email',
        'status',
    ];

    public function weighingTransactions()
    {
        return $this->hasMany(Weighing::class);
    }
}
