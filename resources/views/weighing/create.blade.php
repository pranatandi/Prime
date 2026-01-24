@extends('layouts.app')

@section('title', 'Create Weighing Transaction')

@section('content')
<div class="px-4 sm:px-0">
    <div class="mb-6">
        <a href="{{ route('weighing.index') }}" class="text-sm font-medium text-indigo-600 dark:text-indigo-400 hover:text-indigo-500">
            ← Back to Weighing List
        </a>
        <h1 class="mt-2 text-3xl font-bold text-gray-900 dark:text-white">Create Weighing Transaction</h1>
    </div>

    <div class="bg-white dark:bg-gray-800 shadow rounded-lg">
        <form action="{{ route('weighing.store') }}" method="POST" enctype="multipart/form-data" class="p-6 space-y-6">
            @csrf

            <div class="grid grid-cols-1 gap-6 sm:grid-cols-2">
                <!-- Supplier -->
                <div>
                    <label for="supplier_id" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
                        Supplier <span class="text-red-500">*</span>
                    </label>
                    <select name="supplier_id" id="supplier_id" required
                            class="mt-1 block w-full rounded-md border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm @error('supplier_id') border-red-500 @enderror">
                        <option value="">Select Supplier</option>
                        @foreach($suppliers as $supplier)
                            <option value="{{ $supplier->id }}" {{ old('supplier_id') == $supplier->id ? 'selected' : '' }}>
                                {{ $supplier->name }} ({{ $supplier->code }})
                            </option>
                        @endforeach
                    </select>
                    @error('supplier_id')
                        <p class="mt-1 text-sm text-red-600 dark:text-red-400">{{ $message }}</p>
                    @enderror
                </div>

                <!-- Vehicle -->
                <div>
                    <label for="vehicle_id" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
                        Vehicle <span class="text-red-500">*</span>
                    </label>
                    <select name="vehicle_id" id="vehicle_id" required
                            class="mt-1 block w-full rounded-md border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm @error('vehicle_id') border-red-500 @enderror">
                        <option value="">Select Vehicle</option>
                        @foreach($vehicles as $vehicle)
                            <option value="{{ $vehicle->id }}" {{ old('vehicle_id') == $vehicle->id ? 'selected' : '' }}>
                                {{ $vehicle->license_plate }} - {{ $vehicle->type }}
                            </option>
                        @endforeach
                    </select>
                    @error('vehicle_id')
                        <p class="mt-1 text-sm text-red-600 dark:text-red-400">{{ $message }}</p>
                    @enderror
                </div>

                <!-- Gross Weight -->
                <div>
                    <label for="gross_weight" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
                        Gross Weight (kg) <span class="text-red-500">*</span>
                    </label>
                    <input type="number" step="0.01" name="gross_weight" id="gross_weight" 
                           value="{{ old('gross_weight') }}" required
                           class="mt-1 block w-full rounded-md border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm @error('gross_weight') border-red-500 @enderror">
                    @error('gross_weight')
                        <p class="mt-1 text-sm text-red-600 dark:text-red-400">{{ $message }}</p>
                    @enderror
                </div>

                <!-- Tare Weight -->
                <div>
                    <label for="tare_weight" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
                        Tare Weight (kg) <span class="text-red-500">*</span>
                    </label>
                    <input type="number" step="0.01" name="tare_weight" id="tare_weight" 
                           value="{{ old('tare_weight') }}" required
                           class="mt-1 block w-full rounded-md border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm @error('tare_weight') border-red-500 @enderror">
                    @error('tare_weight')
                        <p class="mt-1 text-sm text-red-600 dark:text-red-400">{{ $message }}</p>
                    @enderror
                </div>

                <!-- Net Weight (Display Only) -->
                <div>
                    <label for="net_weight_display" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
                        Net Weight (kg)
                    </label>
                    <input type="text" id="net_weight_display" readonly
                           value="0.00"
                           class="mt-1 block w-full rounded-md border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white bg-gray-50 dark:bg-gray-600 shadow-sm sm:text-sm">
                    <p class="mt-1 text-xs text-gray-500 dark:text-gray-400">Calculated automatically (Gross - Tare)</p>
                </div>

                <!-- Weighing Time -->
                <div>
                    <label for="weighing_time" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
                        Weighing Time <span class="text-red-500">*</span>
                    </label>
                    <input type="datetime-local" name="weighing_time" id="weighing_time" 
                           value="{{ old('weighing_time', now()->format('Y-m-d\TH:i')) }}" required
                           class="mt-1 block w-full rounded-md border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm @error('weighing_time') border-red-500 @enderror">
                    @error('weighing_time')
                        <p class="mt-1 text-sm text-red-600 dark:text-red-400">{{ $message }}</p>
                    @enderror
                </div>
            </div>

            <!-- Vehicle Photo -->
            <div>
                <label for="vehicle_photo" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
                    Vehicle Photo
                </label>
                <div class="mt-1 flex items-center">
                    <input type="file" name="vehicle_photo" id="vehicle_photo" accept="image/*"
                           class="block w-full text-sm text-gray-500 dark:text-gray-400
                                  file:mr-4 file:py-2 file:px-4
                                  file:rounded-md file:border-0
                                  file:text-sm file:font-semibold
                                  file:bg-indigo-50 dark:file:bg-indigo-900 file:text-indigo-700 dark:file:text-indigo-300
                                  hover:file:bg-indigo-100 dark:hover:file:bg-indigo-800
                                  @error('vehicle_photo') border-red-500 @enderror">
                </div>
                <div id="photo_preview" class="mt-2 hidden">
                    <img id="photo_preview_img" src="" alt="Preview" class="max-w-xs rounded-lg shadow">
                </div>
                @error('vehicle_photo')
                    <p class="mt-1 text-sm text-red-600 dark:text-red-400">{{ $message }}</p>
                @enderror
            </div>

            <!-- Notes -->
            <div>
                <label for="notes" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
                    Notes
                </label>
                <textarea name="notes" id="notes" rows="3"
                          class="mt-1 block w-full rounded-md border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm @error('notes') border-red-500 @enderror">{{ old('notes') }}</textarea>
                @error('notes')
                    <p class="mt-1 text-sm text-red-600 dark:text-red-400">{{ $message }}</p>
                @enderror
            </div>

            <!-- Actions -->
            <div class="flex items-center justify-end gap-3 pt-4 border-t border-gray-200 dark:border-gray-700">
                <a href="{{ route('weighing.index') }}" 
                   class="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm hover:bg-gray-50 dark:hover:bg-gray-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500">
                    Cancel
                </a>
                <button type="submit"
                        class="px-4 py-2 text-sm font-medium text-white bg-indigo-600 border border-transparent rounded-md shadow-sm hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500">
                    Create Transaction
                </button>
            </div>
        </form>
    </div>
</div>

@push('scripts')
<script>
    // Calculate net weight automatically
    function calculateNetWeight() {
        const gross = parseFloat(document.getElementById('gross_weight').value) || 0;
        const tare = parseFloat(document.getElementById('tare_weight').value) || 0;
        const net = gross - tare;
        document.getElementById('net_weight_display').value = net.toFixed(2);
    }

    document.getElementById('gross_weight').addEventListener('input', calculateNetWeight);
    document.getElementById('tare_weight').addEventListener('input', calculateNetWeight);

    // Photo preview
    document.getElementById('vehicle_photo').addEventListener('change', function(e) {
        const file = e.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = function(e) {
                document.getElementById('photo_preview').classList.remove('hidden');
                document.getElementById('photo_preview_img').src = e.target.result;
            };
            reader.readAsDataURL(file);
        }
    });
</script>
@endpush
@endsection
