<?php

namespace Tests\Feature;

use App\Models\Weighing;
use App\Models\Supplier;
use App\Models\Vehicle;
use App\Models\User;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Tests\TestCase;
use Carbon\Carbon;

class WeighingTest extends TestCase
{
    use RefreshDatabase;

    protected function setUp(): void
    {
        parent::setUp();
        
        $this->user = User::factory()->create();
        $this->actingAs($this->user);
    }

    public function test_can_create_weighing_transaction(): void
    {
        $supplier = Supplier::factory()->create();
        $vehicle = Vehicle::factory()->create();

        $weighingData = [
            'supplier_id' => $supplier->id,
            'vehicle_id' => $vehicle->id,
            'vehicle_plate_number' => $vehicle->plate_number,
            'gross_weight' => 5000.50,
            'tare_weight' => 2000.25,
            'weighing_datetime' => Carbon::now()->format('Y-m-d H:i:s'),
            'notes' => 'Test weighing transaction',
        ];

        $response = $this->post(route('weighing.store'), $weighingData);

        $response->assertRedirect(route('weighing.index'));
        $response->assertSessionHas('success', 'Weighing transaction created successfully.');

        $this->assertDatabaseHas('weighing_transactions', [
            'supplier_id' => $supplier->id,
            'vehicle_id' => $vehicle->id,
            'vehicle_plate_number' => $vehicle->plate_number,
            'gross_weight' => 5000.50,
            'tare_weight' => 2000.25,
            'user_id' => $this->user->id,
        ]);
    }

    public function test_net_weight_is_calculated_correctly(): void
    {
        $supplier = Supplier::factory()->create();
        $vehicle = Vehicle::factory()->create();

        $grossWeight = 5000.00;
        $tareWeight = 2000.00;
        $expectedNetWeight = 3000.00;

        $weighingData = [
            'supplier_id' => $supplier->id,
            'vehicle_id' => $vehicle->id,
            'vehicle_plate_number' => $vehicle->plate_number,
            'gross_weight' => $grossWeight,
            'tare_weight' => $tareWeight,
            'weighing_datetime' => Carbon::now()->format('Y-m-d H:i:s'),
        ];

        $this->post(route('weighing.store'), $weighingData);

        $weighing = Weighing::latest()->first();

        $this->assertEquals($expectedNetWeight, $weighing->net_weight);
        $this->assertEquals($grossWeight - $tareWeight, $weighing->net_weight);
    }

    public function test_transaction_code_is_auto_generated(): void
    {
        $supplier = Supplier::factory()->create();
        $vehicle = Vehicle::factory()->create();

        $weighingData = [
            'supplier_id' => $supplier->id,
            'vehicle_id' => $vehicle->id,
            'vehicle_plate_number' => $vehicle->plate_number,
            'gross_weight' => 5000.00,
            'tare_weight' => 2000.00,
            'weighing_datetime' => Carbon::now()->format('Y-m-d H:i:s'),
        ];

        $this->post(route('weighing.store'), $weighingData);

        $weighing = Weighing::latest()->first();
        $today = Carbon::now()->format('Ymd');
        $expectedPattern = "/^WGH-{$today}-\d{4}$/";

        $this->assertMatchesRegularExpression($expectedPattern, $weighing->transaction_code);
        
        $this->post(route('weighing.store'), $weighingData);
        
        $allWeighings = Weighing::orderBy('id', 'desc')->take(2)->get();
        $this->assertNotEquals($allWeighings[0]->transaction_code, $allWeighings[1]->transaction_code);
    }

    public function test_can_list_weighing_transactions(): void
    {
        $supplier = Supplier::factory()->create();
        $vehicle = Vehicle::factory()->create();

        Weighing::factory()->count(3)->create([
            'user_id' => $this->user->id,
            'supplier_id' => $supplier->id,
            'vehicle_id' => $vehicle->id,
            'weighing_datetime' => Carbon::now(),
        ]);

        $response = $this->get(route('weighing.index'));

        $response->assertViewIs('weighing.index');
        $response->assertViewHas('weighings');
        
        $weighings = $response->viewData('weighings');
        $this->assertCount(3, $weighings);
    }

    public function test_can_update_weighing_transaction(): void
    {
        $weighing = Weighing::factory()->create([
            'user_id' => $this->user->id,
        ]);

        $updatedData = [
            'supplier_id' => $weighing->supplier_id,
            'vehicle_id' => $weighing->vehicle_id,
            'vehicle_plate_number' => $weighing->vehicle_plate_number,
            'gross_weight' => 6000.00,
            'tare_weight' => 2500.00,
            'weighing_datetime' => Carbon::now()->format('Y-m-d H:i:s'),
            'notes' => 'Updated notes',
        ];

        $response = $this->put(route('weighing.update', $weighing), $updatedData);

        $response->assertRedirect(route('weighing.index'));
        $response->assertSessionHas('success', 'Weighing transaction updated successfully.');

        $weighing->refresh();

        $this->assertEquals(6000.00, $weighing->gross_weight);
        $this->assertEquals(2500.00, $weighing->tare_weight);
        $this->assertEquals(3500.00, $weighing->net_weight);
        $this->assertEquals('Updated notes', $weighing->notes);
    }

    public function test_can_delete_weighing_transaction(): void
    {
        $weighing = Weighing::factory()->create([
            'user_id' => $this->user->id,
        ]);

        $weighingId = $weighing->id;

        $response = $this->delete(route('weighing.destroy', $weighing));

        $response->assertRedirect(route('weighing.index'));
        $response->assertSessionHas('success', 'Weighing transaction deleted successfully.');

        $this->assertDatabaseMissing('weighing_transactions', [
            'id' => $weighingId,
        ]);
    }
}
