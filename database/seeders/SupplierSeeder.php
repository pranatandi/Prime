<?php

namespace Database\Seeders;

use Illuminate\Database\Console\Seeds\WithoutModelEvents;
use Illuminate\Database\Seeder;

class SupplierSeeder extends Seeder
{
    /**
     * Run the database seeds.
     */
    public function run(): void
    {
        $suppliers = [
            ['name' => 'PT Sawit Jaya', 'code' => 'SUP-0001', 'phone' => '081234567890', 'address' => 'Jl. Raya No. 123, Jakarta', 'email' => 'sawit.jaya@example.com'],
            ['name' => 'CV Maju Bersama', 'code' => 'SUP-0002', 'phone' => '081234567891', 'address' => 'Jl. Sudirman No. 45, Bandung', 'email' => 'maju.bersama@example.com'],
            ['name' => 'Koperasi Tani Sejahtera', 'code' => 'SUP-0003', 'phone' => '081234567892', 'address' => 'Jl. Pemuda No. 78, Surabaya', 'email' => 'tani.sejahtera@example.com'],
            ['name' => 'UD Berkah Sawit', 'code' => 'SUP-0004', 'phone' => '081234567893', 'address' => 'Jl. Gatot Subroto No. 90, Medan', 'email' => 'berkah.sawit@example.com'],
            ['name' => 'PT Agro Nusantara', 'code' => 'SUP-0005', 'phone' => '081234567894', 'address' => 'Jl. Ahmad Yani No. 12, Palembang', 'email' => 'agro.nusantara@example.com'],
        ];

        foreach ($suppliers as $supplier) {
            \App\Models\Supplier::create($supplier);
        }
    }
}
