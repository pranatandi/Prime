<?php

namespace Tests\Feature;

use App\Models\Supplier;
use App\Models\Weighing;
use App\Models\User;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Tests\TestCase;

class SupplierTest extends TestCase
{
    use RefreshDatabase;

    protected function setUp(): void
    {
        parent::setUp();
        
        $this->user = User::factory()->create();
        $this->actingAs($this->user);
    }

    public function test_can_create_supplier(): void
    {
        $supplierData = [
            'name' => 'Test Supplier Corp',
            'phone' => '+1234567890',
            'address' => '123 Test Street, Test City',
            'email' => 'test@supplier.com',
            'status' => 'active',
        ];

        $response = $this->post(route('suppliers.store'), $supplierData);

        $response->assertRedirect(route('suppliers.index'));
        $response->assertSessionHas('success', 'Supplier created successfully.');

        $this->assertDatabaseHas('suppliers', [
            'name' => 'Test Supplier Corp',
            'phone' => '+1234567890',
            'address' => '123 Test Street, Test City',
            'email' => 'test@supplier.com',
            'status' => 'active',
        ]);

        $supplier = Supplier::where('name', 'Test Supplier Corp')->first();
        $this->assertMatchesRegularExpression('/^SUP-\d{4}$/', $supplier->code);
    }

    public function test_supplier_code_is_unique(): void
    {
        $supplier1 = Supplier::factory()->create();
        $supplier2 = Supplier::factory()->create();

        $this->assertNotEquals($supplier1->code, $supplier2->code);

        $this->assertDatabaseCount('suppliers', 2);
    }

    public function test_can_list_suppliers(): void
    {
        Supplier::factory()->count(5)->create();

        $response = $this->get(route('suppliers.index'));

        $response->assertStatus(200);
        $response->assertViewIs('suppliers.index');
        $response->assertViewHas('suppliers');
    }

    public function test_can_update_supplier(): void
    {
        $supplier = Supplier::factory()->create([
            'name' => 'Old Supplier Name',
            'status' => 'active',
        ]);

        $updatedData = [
            'name' => 'Updated Supplier Name',
            'code' => $supplier->code,
            'phone' => '+9876543210',
            'address' => '456 Updated Street',
            'email' => 'updated@supplier.com',
            'status' => 'inactive',
        ];

        $response = $this->put(route('suppliers.update', $supplier), $updatedData);

        $response->assertRedirect(route('suppliers.index'));
        $response->assertSessionHas('success', 'Supplier updated successfully.');

        $supplier->refresh();

        $this->assertEquals('Updated Supplier Name', $supplier->name);
        $this->assertEquals('+9876543210', $supplier->phone);
        $this->assertEquals('456 Updated Street', $supplier->address);
        $this->assertEquals('updated@supplier.com', $supplier->email);
        $this->assertEquals('inactive', $supplier->status);
    }

    public function test_can_delete_supplier_without_transactions(): void
    {
        $supplier = Supplier::factory()->create();

        $supplierId = $supplier->id;

        $response = $this->delete(route('suppliers.destroy', $supplier));

        $response->assertRedirect(route('suppliers.index'));
        $response->assertSessionHas('success', 'Supplier deleted successfully.');

        $this->assertDatabaseMissing('suppliers', [
            'id' => $supplierId,
        ]);
    }

    public function test_cannot_delete_supplier_with_transactions(): void
    {
        $supplier = Supplier::factory()->create();
        
        Weighing::factory()->create([
            'supplier_id' => $supplier->id,
            'user_id' => $this->user->id,
        ]);

        $response = $this->delete(route('suppliers.destroy', $supplier));

        $response->assertRedirect();
        $response->assertSessionHas('error', 'Cannot delete supplier with existing weighing transactions.');

        $this->assertDatabaseHas('suppliers', [
            'id' => $supplier->id,
        ]);
    }
}
