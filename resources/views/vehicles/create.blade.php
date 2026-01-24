@extends('layouts.app')

@section('title', 'Create Vehicle')

@section('content')
<div class="px-4 sm:px-0">
    <div class="mb-6">
        <a href="{{ route('vehicles.index') }}" class="text-sm font-medium text-indigo-600 dark:text-indigo-400 hover:text-indigo-500">
            ← Back to Vehicles List
        </a>
        <h1 class="mt-2 text-3xl font-bold text-gray-900 dark:text-white">Create Vehicle</h1>
    </div>

    <div class="bg-white dark:bg-gray-800 shadow rounded-lg">
        <form action="{{ route('vehicles.store') }}" method="POST" class="p-6 space-y-6">
            @csrf

            <div class="grid grid-cols-1 gap-6 sm:grid-cols-2">
                <!-- License Plate -->
                <div>
                    <label for="license_plate" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
                        License Plate <span class="text-red-500">*</span>
                    </label>
                    <input type="text" name="license_plate" id="license_plate" value="{{ old('license_plate') }}" required
                           class="mt-1 block w-full rounded-md border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm @error('license_plate') border-red-500 @enderror">
                    @error('license_plate')
                        <p class="mt-1 text-sm text-red-600 dark:text-red-400">{{ $message }}</p>
                    @enderror
                </div>

                <!-- Type -->
                <div>
                    <label for="type" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
                        Type <span class="text-red-500">*</span>
                    </label>
                    <select name="type" id="type" required
                            class="mt-1 block w-full rounded-md border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm @error('type') border-red-500 @enderror">
                        <option value="">Select Type</option>
                        <option value="Truck" {{ old('type') == 'Truck' ? 'selected' : '' }}>Truck</option>
                        <option value="Pickup" {{ old('type') == 'Pickup' ? 'selected' : '' }}>Pickup</option>
                        <option value="Van" {{ old('type') == 'Van' ? 'selected' : '' }}>Van</option>
                        <option value="Trailer" {{ old('type') == 'Trailer' ? 'selected' : '' }}>Trailer</option>
                        <option value="Other" {{ old('type') == 'Other' ? 'selected' : '' }}>Other</option>
                    </select>
                    @error('type')
                        <p class="mt-1 text-sm text-red-600 dark:text-red-400">{{ $message }}</p>
                    @enderror
                </div>

                <!-- Driver Name -->
                <div>
                    <label for="driver_name" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
                        Driver Name
                    </label>
                    <input type="text" name="driver_name" id="driver_name" value="{{ old('driver_name') }}"
                           class="mt-1 block w-full rounded-md border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm @error('driver_name') border-red-500 @enderror">
                    @error('driver_name')
                        <p class="mt-1 text-sm text-red-600 dark:text-red-400">{{ $message }}</p>
                    @enderror
                </div>

                <!-- Driver Phone -->
                <div>
                    <label for="driver_phone" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
                        Driver Phone
                    </label>
                    <input type="text" name="driver_phone" id="driver_phone" value="{{ old('driver_phone') }}"
                           class="mt-1 block w-full rounded-md border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm @error('driver_phone') border-red-500 @enderror">
                    @error('driver_phone')
                        <p class="mt-1 text-sm text-red-600 dark:text-red-400">{{ $message }}</p>
                    @enderror
                </div>

                <!-- Capacity -->
                <div>
                    <label for="capacity" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
                        Capacity (kg)
                    </label>
                    <input type="number" step="0.01" name="capacity" id="capacity" value="{{ old('capacity') }}"
                           class="mt-1 block w-full rounded-md border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm @error('capacity') border-red-500 @enderror">
                    @error('capacity')
                        <p class="mt-1 text-sm text-red-600 dark:text-red-400">{{ $message }}</p>
                    @enderror
                </div>
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
                <a href="{{ route('vehicles.index') }}" 
                   class="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm hover:bg-gray-50 dark:hover:bg-gray-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500">
                    Cancel
                </a>
                <button type="submit"
                        class="px-4 py-2 text-sm font-medium text-white bg-indigo-600 border border-transparent rounded-md shadow-sm hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500">
                    Create Vehicle
                </button>
            </div>
        </form>
    </div>
</div>
@endsection
