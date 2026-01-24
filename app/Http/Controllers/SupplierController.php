<?php

namespace App\Http\Controllers;

use App\Models\Supplier;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\DB;

class SupplierController extends Controller
{
    /**
     * Display a listing of the suppliers.
     *
     * @return \Illuminate\View\View
     */
    public function index()
    {
        $suppliers = Supplier::orderBy('created_at', 'desc')->paginate(15);

        return view('suppliers.index', compact('suppliers'));
    }

    /**
     * Show the form for creating a new supplier.
     *
     * @return \Illuminate\View\View
     */
    public function create()
    {
        return view('suppliers.create');
    }

    /**
     * Store a newly created supplier in storage.
     *
     * @param Request $request
     * @return \Illuminate\Http\RedirectResponse
     */
    public function store(Request $request)
    {
        $validated = $request->validate([
            'name' => 'required|string|max:255',
            'phone' => 'nullable|string|max:20',
            'address' => 'nullable|string|max:500',
            'email' => 'nullable|email|max:255',
            'status' => 'nullable|in:active,inactive',
        ]);

        try {
            DB::beginTransaction();

            // Generate unique supplier code (format: SUP-XXXX)
            $validated['code'] = $this->generateSupplierCode();
            
            // Set default status if not provided
            $validated['status'] = $validated['status'] ?? 'active';

            Supplier::create($validated);

            DB::commit();

            return redirect()->route('suppliers.index')
                ->with('success', 'Supplier created successfully.');
        } catch (\Exception $e) {
            DB::rollBack();

            return redirect()->back()
                ->withInput()
                ->with('error', 'Failed to create supplier: ' . $e->getMessage());
        }
    }

    /**
     * Display the specified supplier.
     *
     * @param Supplier $supplier
     * @return \Illuminate\View\View
     */
    public function show(Supplier $supplier)
    {
        $supplier->load('weighingTransactions');

        return view('suppliers.show', compact('supplier'));
    }

    /**
     * Show the form for editing the specified supplier.
     *
     * @param Supplier $supplier
     * @return \Illuminate\View\View
     */
    public function edit(Supplier $supplier)
    {
        return view('suppliers.edit', compact('supplier'));
    }

    /**
     * Update the specified supplier in storage.
     *
     * @param Request $request
     * @param Supplier $supplier
     * @return \Illuminate\Http\RedirectResponse
     */
    public function update(Request $request, Supplier $supplier)
    {
        $validated = $request->validate([
            'name' => 'required|string|max:255',
            'code' => 'required|string|max:50|unique:suppliers,code,' . $supplier->id,
            'phone' => 'nullable|string|max:20',
            'address' => 'nullable|string|max:500',
            'email' => 'nullable|email|max:255',
            'status' => 'required|in:active,inactive',
        ]);

        try {
            $supplier->update($validated);

            return redirect()->route('suppliers.index')
                ->with('success', 'Supplier updated successfully.');
        } catch (\Exception $e) {
            return redirect()->back()
                ->withInput()
                ->with('error', 'Failed to update supplier: ' . $e->getMessage());
        }
    }

    /**
     * Remove the specified supplier from storage.
     *
     * @param Supplier $supplier
     * @return \Illuminate\Http\RedirectResponse
     */
    public function destroy(Supplier $supplier)
    {
        try {
            // Check if supplier has weighing transactions
            if ($supplier->weighingTransactions()->count() > 0) {
                return redirect()->back()
                    ->with('error', 'Cannot delete supplier with existing weighing transactions.');
            }

            $supplier->delete();

            return redirect()->route('suppliers.index')
                ->with('success', 'Supplier deleted successfully.');
        } catch (\Exception $e) {
            return redirect()->back()
                ->with('error', 'Failed to delete supplier: ' . $e->getMessage());
        }
    }

    /**
     * Generate unique supplier code with format: SUP-XXXX
     *
     * @return string
     */
    private function generateSupplierCode(): string
    {
        $prefix = 'SUP-';

        // Get the last supplier code
        $lastSupplier = Supplier::where('code', 'like', $prefix . '%')
            ->orderBy('code', 'desc')
            ->first();

        if ($lastSupplier) {
            // Extract the sequence number and increment
            $lastSequence = (int) substr($lastSupplier->code, strlen($prefix));
            $newSequence = $lastSequence + 1;
        } else {
            $newSequence = 1;
        }

        // Format with leading zeros (4 digits)
        return $prefix . str_pad($newSequence, 4, '0', STR_PAD_LEFT);
    }
}
