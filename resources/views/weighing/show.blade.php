@extends('layouts.app')

@section('title', 'Weighing Details')

@section('content')
<div class="px-4 sm:px-0">
    <div class="mb-6">
        <a href="{{ route('weighing.index') }}" class="text-sm font-medium text-indigo-600 dark:text-indigo-400 hover:text-indigo-500">
            ← Back to Weighing List
        </a>
        <div class="mt-2 flex items-center justify-between">
            <h1 class="text-3xl font-bold text-gray-900 dark:text-white">Weighing Details</h1>
            <div class="flex gap-3">
                <a href="{{ route('weighing.edit', $weighing->id) }}" 
                   class="inline-flex items-center px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm text-sm font-medium text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-700 hover:bg-gray-50 dark:hover:bg-gray-600">
                    Edit
                </a>
                <form action="{{ route('weighing.destroy', $weighing->id) }}" method="POST" class="inline">
                    @csrf
                    @method('DELETE')
                    <button type="submit" 
                            onclick="return confirm('Are you sure you want to delete this weighing transaction?')"
                            class="inline-flex items-center px-4 py-2 border border-red-300 dark:border-red-600 rounded-md shadow-sm text-sm font-medium text-red-700 dark:text-red-300 bg-white dark:bg-gray-700 hover:bg-red-50 dark:hover:bg-red-900/20">
                        Delete
                    </button>
                </form>
            </div>
        </div>
    </div>

    <div class="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <!-- Main Information -->
        <div class="lg:col-span-2 space-y-6">
            <div class="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
                <h2 class="text-lg font-medium text-gray-900 dark:text-white mb-4">Transaction Information</h2>
                <dl class="grid grid-cols-1 gap-x-4 gap-y-6 sm:grid-cols-2">
                    <div>
                        <dt class="text-sm font-medium text-gray-500 dark:text-gray-400">Transaction Code</dt>
                        <dd class="mt-1 text-sm text-gray-900 dark:text-white font-semibold">{{ $weighing->transaction_code }}</dd>
                    </div>
                    <div>
                        <dt class="text-sm font-medium text-gray-500 dark:text-gray-400">Weighing Time</dt>
                        <dd class="mt-1 text-sm text-gray-900 dark:text-white">{{ $weighing->weighing_time->format('Y-m-d H:i:s') }}</dd>
                    </div>
                    <div>
                        <dt class="text-sm font-medium text-gray-500 dark:text-gray-400">Supplier</dt>
                        <dd class="mt-1 text-sm text-gray-900 dark:text-white">
                            <a href="{{ route('suppliers.show', $weighing->supplier->id) }}" class="text-indigo-600 dark:text-indigo-400 hover:text-indigo-900 dark:hover:text-indigo-300">
                                {{ $weighing->supplier->name }} ({{ $weighing->supplier->code }})
                            </a>
                        </dd>
                    </div>
                    <div>
                        <dt class="text-sm font-medium text-gray-500 dark:text-gray-400">Vehicle</dt>
                        <dd class="mt-1 text-sm text-gray-900 dark:text-white">
                            <a href="{{ route('vehicles.show', $weighing->vehicle->id) }}" class="text-indigo-600 dark:text-indigo-400 hover:text-indigo-900 dark:hover:text-indigo-300">
                                {{ $weighing->vehicle->license_plate }} - {{ $weighing->vehicle->type }}
                            </a>
                        </dd>
                    </div>
                </dl>
            </div>

            <!-- Weight Information -->
            <div class="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
                <h2 class="text-lg font-medium text-gray-900 dark:text-white mb-4">Weight Measurements</h2>
                <div class="grid grid-cols-1 gap-6 sm:grid-cols-3">
                    <div class="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-4">
                        <dt class="text-sm font-medium text-blue-600 dark:text-blue-400">Gross Weight</dt>
                        <dd class="mt-2 text-2xl font-semibold text-blue-900 dark:text-blue-300">{{ number_format($weighing->gross_weight, 2) }}</dd>
                        <dd class="text-sm text-blue-600 dark:text-blue-400">kg</dd>
                    </div>
                    <div class="bg-yellow-50 dark:bg-yellow-900/20 rounded-lg p-4">
                        <dt class="text-sm font-medium text-yellow-600 dark:text-yellow-400">Tare Weight</dt>
                        <dd class="mt-2 text-2xl font-semibold text-yellow-900 dark:text-yellow-300">{{ number_format($weighing->tare_weight, 2) }}</dd>
                        <dd class="text-sm text-yellow-600 dark:text-yellow-400">kg</dd>
                    </div>
                    <div class="bg-green-50 dark:bg-green-900/20 rounded-lg p-4">
                        <dt class="text-sm font-medium text-green-600 dark:text-green-400">Net Weight</dt>
                        <dd class="mt-2 text-2xl font-semibold text-green-900 dark:text-green-300">{{ number_format($weighing->net_weight, 2) }}</dd>
                        <dd class="text-sm text-green-600 dark:text-green-400">kg</dd>
                    </div>
                </div>
            </div>

            <!-- Notes -->
            @if($weighing->notes)
            <div class="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
                <h2 class="text-lg font-medium text-gray-900 dark:text-white mb-4">Notes</h2>
                <p class="text-sm text-gray-700 dark:text-gray-300 whitespace-pre-wrap">{{ $weighing->notes }}</p>
            </div>
            @endif
        </div>

        <!-- Sidebar -->
        <div class="space-y-6">
            <!-- Vehicle Photo -->
            @if($weighing->vehicle_photo)
            <div class="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
                <h2 class="text-lg font-medium text-gray-900 dark:text-white mb-4">Vehicle Photo</h2>
                <img src="{{ asset('storage/' . $weighing->vehicle_photo) }}" alt="Vehicle Photo" class="w-full rounded-lg shadow-md">
            </div>
            @endif

            <!-- Metadata -->
            <div class="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
                <h2 class="text-lg font-medium text-gray-900 dark:text-white mb-4">Metadata</h2>
                <dl class="space-y-3">
                    <div>
                        <dt class="text-xs font-medium text-gray-500 dark:text-gray-400">Created At</dt>
                        <dd class="mt-1 text-sm text-gray-900 dark:text-white">{{ $weighing->created_at->format('Y-m-d H:i:s') }}</dd>
                    </div>
                    <div>
                        <dt class="text-xs font-medium text-gray-500 dark:text-gray-400">Updated At</dt>
                        <dd class="mt-1 text-sm text-gray-900 dark:text-white">{{ $weighing->updated_at->format('Y-m-d H:i:s') }}</dd>
                    </div>
                    @if($weighing->user)
                    <div>
                        <dt class="text-xs font-medium text-gray-500 dark:text-gray-400">Created By</dt>
                        <dd class="mt-1 text-sm text-gray-900 dark:text-white">{{ $weighing->user->name }}</dd>
                    </div>
                    @endif
                </dl>
            </div>
        </div>
    </div>
</div>
@endsection
