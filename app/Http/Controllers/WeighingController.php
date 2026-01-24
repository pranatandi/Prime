<?php

namespace App\Http\Controllers;

use App\Models\Weighing;
use App\Models\Supplier;
use App\Models\Vehicle;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Storage;
use Carbon\Carbon;

class WeighingController extends Controller
{
    /**
     * Display a listing of the weighing transactions.
     *
     * @return \Illuminate\View\View
     */
    public function index()
    {
        $weighings = Weighing::with(['supplier', 'vehicle', 'user'])
            ->orderBy('weighing_datetime', 'desc')
            ->paginate(15);

        return view('weighing.index', compact('weighings'));
    }

    /**
     * Show the form for creating a new weighing transaction.
     *
     * @return \Illuminate\View\View
     */
    public function create()
    {
        $suppliers = Supplier::where('status', 'active')->get();
        $vehicles = Vehicle::where('status', 'active')->get();

        return view('weighing.create', compact('suppliers', 'vehicles'));
    }

    /**
     * Store a newly created weighing transaction in storage.
     *
     * @param Request $request
     * @return \Illuminate\Http\RedirectResponse
     */
    public function store(Request $request)
    {
        $validated = $request->validate([
            'supplier_id' => 'required|exists:suppliers,id',
            'vehicle_id' => 'required|exists:vehicles,id',
            'vehicle_plate_number' => 'required|string|max:20',
            'gross_weight' => 'required|numeric|min:0',
            'tare_weight' => 'required|numeric|min:0',
            'weighing_datetime' => 'required|date',
            'vehicle_photo' => 'nullable|image|mimes:jpeg,png,jpg|max:2048',
            'notes' => 'nullable|string|max:1000',
        ]);

        try {
            DB::beginTransaction();

            // Generate unique transaction code (format: WGH-YYYYMMDD-XXXX)
            $validated['transaction_code'] = $this->generateTransactionCode();

            // Calculate net weight
            $validated['net_weight'] = $validated['gross_weight'] - $validated['tare_weight'];

            // Handle vehicle photo upload if present
            if ($request->hasFile('vehicle_photo')) {
                $path = $request->file('vehicle_photo')->store('weighing/photos', 'public');
                $validated['vehicle_photo'] = $path;
            }

            // Set user_id from authenticated user
            $validated['user_id'] = auth()->id();

            Weighing::create($validated);

            DB::commit();

            return redirect()->route('weighing.index')
                ->with('success', 'Weighing transaction created successfully.');
        } catch (\Exception $e) {
            DB::rollBack();

            return redirect()->back()
                ->withInput()
                ->with('error', 'Failed to create weighing transaction: ' . $e->getMessage());
        }
    }

    /**
     * Display the specified weighing transaction.
     *
     * @param Weighing $weighing
     * @return \Illuminate\View\View
     */
    public function show(Weighing $weighing)
    {
        $weighing->load(['supplier', 'vehicle', 'user']);

        return view('weighing.show', compact('weighing'));
    }

    /**
     * Show the form for editing the specified weighing transaction.
     *
     * @param Weighing $weighing
     * @return \Illuminate\View\View
     */
    public function edit(Weighing $weighing)
    {
        $suppliers = Supplier::where('status', 'active')->get();
        $vehicles = Vehicle::where('status', 'active')->get();

        return view('weighing.edit', compact('weighing', 'suppliers', 'vehicles'));
    }

    /**
     * Update the specified weighing transaction in storage.
     *
     * @param Request $request
     * @param Weighing $weighing
     * @return \Illuminate\Http\RedirectResponse
     */
    public function update(Request $request, Weighing $weighing)
    {
        $validated = $request->validate([
            'supplier_id' => 'required|exists:suppliers,id',
            'vehicle_id' => 'required|exists:vehicles,id',
            'vehicle_plate_number' => 'required|string|max:20',
            'gross_weight' => 'required|numeric|min:0',
            'tare_weight' => 'required|numeric|min:0',
            'weighing_datetime' => 'required|date',
            'vehicle_photo' => 'nullable|image|mimes:jpeg,png,jpg|max:2048',
            'notes' => 'nullable|string|max:1000',
        ]);

        try {
            DB::beginTransaction();

            // Calculate net weight
            $validated['net_weight'] = $validated['gross_weight'] - $validated['tare_weight'];

            // Handle vehicle photo upload if present
            if ($request->hasFile('vehicle_photo')) {
                // Delete old photo if exists
                if ($weighing->vehicle_photo) {
                    Storage::disk('public')->delete($weighing->vehicle_photo);
                }
                
                $path = $request->file('vehicle_photo')->store('weighing/photos', 'public');
                $validated['vehicle_photo'] = $path;
            }

            $weighing->update($validated);

            DB::commit();

            return redirect()->route('weighing.index')
                ->with('success', 'Weighing transaction updated successfully.');
        } catch (\Exception $e) {
            DB::rollBack();

            return redirect()->back()
                ->withInput()
                ->with('error', 'Failed to update weighing transaction: ' . $e->getMessage());
        }
    }

    /**
     * Remove the specified weighing transaction from storage.
     *
     * @param Weighing $weighing
     * @return \Illuminate\Http\RedirectResponse
     */
    public function destroy(Weighing $weighing)
    {
        try {
            // Delete vehicle photo if exists
            if ($weighing->vehicle_photo) {
                Storage::disk('public')->delete($weighing->vehicle_photo);
            }

            $weighing->delete();

            return redirect()->route('weighing.index')
                ->with('success', 'Weighing transaction deleted successfully.');
        } catch (\Exception $e) {
            return redirect()->back()
                ->with('error', 'Failed to delete weighing transaction: ' . $e->getMessage());
        }
    }

    /**
     * Generate unique transaction code with format: WGH-YYYYMMDD-XXXX
     * 
     * Note: For production with high volume, consider adding a database index
     * on transaction_code column or using database sequences for better performance.
     *
     * @return string
     */
    private function generateTransactionCode(): string
    {
        $date = Carbon::now()->format('Ymd');
        $prefix = "WGH-{$date}-";

        // Get the last transaction code for today with optimized query
        // Uses selective column retrieval for better performance
        $lastTransaction = Weighing::select('transaction_code')
            ->where('transaction_code', 'like', $prefix . '%')
            ->orderBy('transaction_code', 'desc')
            ->first();

        if ($lastTransaction) {
            // Extract the sequence number and increment
            $lastSequence = (int) substr($lastTransaction->transaction_code, -4);
            $newSequence = $lastSequence + 1;
        } else {
            $newSequence = 1;
        }

        // Format with leading zeros (4 digits)
        return $prefix . str_pad($newSequence, 4, '0', STR_PAD_LEFT);
    }
}
