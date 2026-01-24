<?php

use Illuminate\Support\Facades\Route;
use App\Http\Controllers\DashboardController;
use App\Http\Controllers\WeighingController;
use App\Http\Controllers\SupplierController;
use App\Http\Controllers\VehicleController;

// Welcome page
Route::get('/', function () {
    return view('welcome');
});

// Dashboard
Route::get('/dashboard', [DashboardController::class, 'index'])->name('dashboard');

// Weighing Transactions
Route::resource('weighing', WeighingController::class);

// Suppliers
Route::resource('suppliers', SupplierController::class);

// Vehicles
Route::resource('vehicles', VehicleController::class);

// Audit Logs (activity logs from Spatie)
Route::get('/audit-logs', function () {
    $activities = \Spatie\Activitylog\Models\Activity::with('causer', 'subject')
        ->latest()
        ->paginate(20);
    return view('audit-logs.index', compact('activities'));
})->name('audit-logs.index');
