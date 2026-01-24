<?php

namespace Database\Factories;

use App\Models\Weighing;
use App\Models\Supplier;
use App\Models\Vehicle;
use App\Models\User;
use Illuminate\Database\Eloquent\Factories\Factory;
use Carbon\Carbon;

class WeighingFactory extends Factory
{
    protected $model = Weighing::class;

    public function definition(): array
    {
        $grossWeight = $this->faker->randomFloat(2, 1000, 5000);
        $tareWeight = $this->faker->randomFloat(2, 500, 1000);
        $netWeight = $grossWeight - $tareWeight;

        return [
            'transaction_code' => 'WGH-' . date('Ymd') . '-' . str_pad($this->faker->unique()->numberBetween(1, 9999), 4, '0', STR_PAD_LEFT),
            'supplier_id' => Supplier::factory(),
            'vehicle_id' => Vehicle::factory(),
            'vehicle_plate_number' => strtoupper($this->faker->bothify('??-####-??')),
            'gross_weight' => $grossWeight,
            'tare_weight' => $tareWeight,
            'net_weight' => $netWeight,
            'weighing_datetime' => Carbon::now(),
            'vehicle_photo' => null,
            'notes' => $this->faker->optional()->sentence(),
            'user_id' => User::factory(),
        ];
    }
}
