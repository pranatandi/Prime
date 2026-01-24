<?php

namespace Database\Seeders;

use Illuminate\Database\Console\Seeds\WithoutModelEvents;
use Illuminate\Database\Seeder;

class VehicleSeeder extends Seeder
{
    /**
     * Run the database seeds.
     */
    public function run(): void
    {
        $vehicles = [
            ['plate_number' => 'B 1234 XYZ', 'type' => 'Truck', 'driver_name' => 'Ahmad', 'driver_phone' => '08123456789'],
            ['plate_number' => 'D 5678 ABC', 'type' => 'Truck', 'driver_name' => 'Budi', 'driver_phone' => '08123456788'],
            ['plate_number' => 'F 9012 DEF', 'type' => 'Truck', 'driver_name' => 'Candra', 'driver_phone' => '08123456787'],
            ['plate_number' => 'L 3456 GHI', 'type' => 'Truck', 'driver_name' => 'Dedi', 'driver_phone' => '08123456786'],
            ['plate_number' => 'BK 7890 JKL', 'type' => 'Truck', 'driver_name' => 'Eko', 'driver_phone' => '08123456785'],
            ['plate_number' => 'BB 1357 MNO', 'type' => 'Pickup', 'driver_name' => 'Fahmi', 'driver_phone' => '08123456784'],
            ['plate_number' => 'BA 2468 PQR', 'type' => 'Pickup', 'driver_name' => 'Gani', 'driver_phone' => '08123456783'],
        ];

        foreach ($vehicles as $vehicle) {
            \App\Models\Vehicle::create($vehicle);
        }
    }
}
