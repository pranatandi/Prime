<?php

namespace App\Http\Controllers;

use App\Models\Vehicle;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\DB;

class VehicleController extends Controller
{
    /**
     * Display a listing of the vehicles.
     *
     * @return \Illuminate\View\View
     */
    public function index()
    {
        $vehicles = Vehicle::orderBy('created_at', 'desc')->paginate(15);

        return view('vehicles.index', compact('vehicles'));
    }

    /**
     * Show the form for creating a new vehicle.
     *
     * @return \Illuminate\View\View
     */
    public function create()
    {
        return view('vehicles.create');
    }

    /**
     * Store a newly created vehicle in storage.
     *
     * @param Request $request
     * @return \Illuminate\Http\RedirectResponse
     */
    public function store(Request $request)
    {
        $validated = $request->validate([
            'plate_number' => 'required|string|max:20|unique:vehicles,plate_number',
            'type' => 'required|string|max:100',
            'driver_name' => 'nullable|string|max:255',
            'driver_phone' => 'nullable|string|max:20',
            'status' => 'nullable|in:active,inactive',
        ]);

        try {
            // Set default status if not provided
            $validated['status'] = $validated['status'] ?? 'active';

            Vehicle::create($validated);

            return redirect()->route('vehicles.index')
                ->with('success', 'Vehicle created successfully.');
        } catch (\Exception $e) {
            return redirect()->back()
                ->withInput()
                ->with('error', 'Failed to create vehicle: ' . $e->getMessage());
        }
    }

    /**
     * Display the specified vehicle.
     *
     * @param Vehicle $vehicle
     * @return \Illuminate\View\View
     */
    public function show(Vehicle $vehicle)
    {
        $vehicle->load('weighingTransactions');

        return view('vehicles.show', compact('vehicle'));
    }

    /**
     * Show the form for editing the specified vehicle.
     *
     * @param Vehicle $vehicle
     * @return \Illuminate\View\View
     */
    public function edit(Vehicle $vehicle)
    {
        return view('vehicles.edit', compact('vehicle'));
    }

    /**
     * Update the specified vehicle in storage.
     *
     * @param Request $request
     * @param Vehicle $vehicle
     * @return \Illuminate\Http\RedirectResponse
     */
    public function update(Request $request, Vehicle $vehicle)
    {
        $validated = $request->validate([
            'plate_number' => 'required|string|max:20|unique:vehicles,plate_number,' . $vehicle->id,
            'type' => 'required|string|max:100',
            'driver_name' => 'nullable|string|max:255',
            'driver_phone' => 'nullable|string|max:20',
            'status' => 'required|in:active,inactive',
        ]);

        try {
            $vehicle->update($validated);

            return redirect()->route('vehicles.index')
                ->with('success', 'Vehicle updated successfully.');
        } catch (\Exception $e) {
            return redirect()->back()
                ->withInput()
                ->with('error', 'Failed to update vehicle: ' . $e->getMessage());
        }
    }

    /**
     * Remove the specified vehicle from storage.
     *
     * @param Vehicle $vehicle
     * @return \Illuminate\Http\RedirectResponse
     */
    public function destroy(Vehicle $vehicle)
    {
        try {
            // Check if vehicle has weighing transactions
            if ($vehicle->weighingTransactions()->count() > 0) {
                return redirect()->back()
                    ->with('error', 'Cannot delete vehicle with existing weighing transactions.');
            }

            $vehicle->delete();

            return redirect()->route('vehicles.index')
                ->with('success', 'Vehicle deleted successfully.');
        } catch (\Exception $e) {
            return redirect()->back()
                ->with('error', 'Failed to delete vehicle: ' . $e->getMessage());
        }
    }
}
