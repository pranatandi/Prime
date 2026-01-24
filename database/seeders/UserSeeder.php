<?php

namespace Database\Seeders;

use Illuminate\Database\Console\Seeds\WithoutModelEvents;
use Illuminate\Database\Seeder;

class UserSeeder extends Seeder
{
    /**
     * Run the database seeds.
     */
    public function run(): void
    {
        \App\Models\User::create([
            'name' => 'Admin User',
            'email' => 'admin@prime.com',
            'password' => bcrypt('password'),
            'role' => 'admin',
        ]);

        \App\Models\User::create([
            'name' => 'Operator User',
            'email' => 'operator@prime.com',
            'password' => bcrypt('password'),
            'role' => 'operator',
        ]);

        \App\Models\User::create([
            'name' => 'Viewer User',
            'email' => 'viewer@prime.com',
            'password' => bcrypt('password'),
            'role' => 'viewer',
        ]);
    }
}
