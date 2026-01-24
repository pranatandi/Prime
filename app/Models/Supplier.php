<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use App\Traits\Auditable;

class Supplier extends Model
{
    use Auditable;

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
