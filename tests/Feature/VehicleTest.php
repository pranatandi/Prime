<?php

namespace Tests\Feature;

use App\Models\Vehicle;
use App\Models\Weighing;
use App\Models\User;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Tests\TestCase;

class VehicleTest extends TestCase
{
    use RefreshDatabase;

    protected function setUp(): void
    {
        parent::setUp();
        
        $this->user = User::factory()->create();
        $this->actingAs($this->user);
    }

    public function test_can_create_vehicle(): void
    {
        $vehicleData = [
            'plate_number' => 'AB-1234-CD',
            'type' => 'Truck',
            'driver_name' => 'John Doe',
            'driver_phone' => '+1234567890',
            'status' => 'active',
        ];

        $response = $this->post(route('vehicles.store'), $vehicleData);

        $response->assertRedirect(route('vehicles.index'));
        $response->assertSessionHas('success', 'Vehicle created successfully.');

        $this->assertDatabaseHas('vehicles', [
            'plate_number' => 'AB-1234-CD',
            'type' => 'Truck',
            'driver_name' => 'John Doe',
            'driver_phone' => '+1234567890',
            'status' => 'active',
        ]);
    }

    public function test_plate_number_is_unique(): void
    {
        $vehicle1 = Vehicle::factory()->create([
            'plate_number' => 'XY-9999-ZZ',
        ]);

        $vehicleData = [
            'plate_number' => 'XY-9999-ZZ',
            'type' => 'Van',
            'status' => 'active',
        ];

        $response = $this->post(route('vehicles.store'), $vehicleData);

        $response->assertSessionHasErrors('plate_number');

        $this->assertDatabaseCount('vehicles', 1);
    }

    public function test_can_list_vehicles(): void
    {
        Vehicle::factory()->count(5)->create();

        $response = $this->get(route('vehicles.index'));

        $response->assertStatus(200);
        $response->assertViewIs('vehicles.index');
        $response->assertViewHas('vehicles');
    }

    public function test_can_update_vehicle(): void
    {
        $vehicle = Vehicle::factory()->create([
            'plate_number' => 'OLD-1234-PLT',
            'type' => 'Van',
            'status' => 'active',
        ]);

        $updatedData = [
            'plate_number' => 'NEW-5678-PLT',
            'type' => 'Truck',
            'driver_name' => 'Jane Smith',
            'driver_phone' => '+9876543210',
            'status' => 'inactive',
        ];

        $response = $this->put(route('vehicles.update', $vehicle), $updatedData);

        $response->assertRedirect(route('vehicles.index'));
        $response->assertSessionHas('success', 'Vehicle updated successfully.');

        $vehicle->refresh();

        $this->assertEquals('NEW-5678-PLT', $vehicle->plate_number);
        $this->assertEquals('Truck', $vehicle->type);
        $this->assertEquals('Jane Smith', $vehicle->driver_name);
        $this->assertEquals('+9876543210', $vehicle->driver_phone);
        $this->assertEquals('inactive', $vehicle->status);
    }

    public function test_can_delete_vehicle_without_transactions(): void
    {
        $vehicle = Vehicle::factory()->create();

        $vehicleId = $vehicle->id;

        $response = $this->delete(route('vehicles.destroy', $vehicle));

        $response->assertRedirect(route('vehicles.index'));
        $response->assertSessionHas('success', 'Vehicle deleted successfully.');

        $this->assertDatabaseMissing('vehicles', [
            'id' => $vehicleId,
        ]);
    }

    public function test_cannot_delete_vehicle_with_transactions(): void
    {
        $vehicle = Vehicle::factory()->create();
        
        Weighing::factory()->create([
            'vehicle_id' => $vehicle->id,
            'user_id' => $this->user->id,
        ]);

        $response = $this->delete(route('vehicles.destroy', $vehicle));

        $response->assertRedirect();
        $response->assertSessionHas('error', 'Cannot delete vehicle with existing weighing transactions.');

        $this->assertDatabaseHas('vehicles', [
            'id' => $vehicle->id,
        ]);
    }
}
