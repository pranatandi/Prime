@extends('layouts.app')

@section('title', 'Audit Logs')

@section('content')
<div class="px-4 sm:px-0">
    <div class="mb-6">
        <h1 class="text-3xl font-bold text-gray-900 dark:text-white">Audit Logs</h1>
        <p class="mt-2 text-sm text-gray-700 dark:text-gray-300">View all system activities and changes</p>
    </div>

    <!-- Filters -->
    <div class="bg-white dark:bg-gray-800 shadow rounded-lg mb-6 p-4">
        <form method="GET" action="{{ route('audit-logs.index') }}" class="grid grid-cols-1 gap-4 sm:grid-cols-4">
            <div>
                <label for="event" class="block text-sm font-medium text-gray-700 dark:text-gray-300">Event Type</label>
                <select name="event" id="event" 
                        class="mt-1 block w-full rounded-md border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm">
                    <option value="">All Events</option>
                    <option value="created" {{ request('event') == 'created' ? 'selected' : '' }}>Created</option>
                    <option value="updated" {{ request('event') == 'updated' ? 'selected' : '' }}>Updated</option>
                    <option value="deleted" {{ request('event') == 'deleted' ? 'selected' : '' }}>Deleted</option>
                </select>
            </div>
            <div>
                <label for="auditable_type" class="block text-sm font-medium text-gray-700 dark:text-gray-300">Model</label>
                <select name="auditable_type" id="auditable_type" 
                        class="mt-1 block w-full rounded-md border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm">
                    <option value="">All Models</option>
                    <option value="App\Models\Weighing" {{ request('auditable_type') == 'App\Models\Weighing' ? 'selected' : '' }}>Weighing</option>
                    <option value="App\Models\Supplier" {{ request('auditable_type') == 'App\Models\Supplier' ? 'selected' : '' }}>Supplier</option>
                    <option value="App\Models\Vehicle" {{ request('auditable_type') == 'App\Models\Vehicle' ? 'selected' : '' }}>Vehicle</option>
                </select>
            </div>
            <div>
                <label for="date_from" class="block text-sm font-medium text-gray-700 dark:text-gray-300">Date From</label>
                <input type="date" name="date_from" id="date_from" value="{{ request('date_from') }}" 
                       class="mt-1 block w-full rounded-md border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm">
            </div>
            <div class="flex items-end">
                <button type="submit" 
                        class="w-full inline-flex justify-center items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500">
                    Filter
                </button>
            </div>
        </form>
    </div>

    <!-- Audit Logs Table -->
    <div class="bg-white dark:bg-gray-800 shadow rounded-lg overflow-hidden">
        <div class="overflow-x-auto">
            <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
                <thead class="bg-gray-50 dark:bg-gray-900">
                    <tr>
                        <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Timestamp</th>
                        <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">User</th>
                        <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Event</th>
                        <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Model</th>
                        <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Changes</th>
                        <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">IP Address</th>
                    </tr>
                </thead>
                <tbody class="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
                    @forelse($audits as $audit)
                        <tr>
                            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                                {{ $audit->created_at->format('Y-m-d H:i:s') }}
                            </td>
                            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                                {{ $audit->user->name ?? 'System' }}
                            </td>
                            <td class="px-6 py-4 whitespace-nowrap">
                                @if($audit->event == 'created')
                                    <span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-400">
                                        Created
                                    </span>
                                @elseif($audit->event == 'updated')
                                    <span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-blue-100 text-blue-800 dark:bg-blue-900/20 dark:text-blue-400">
                                        Updated
                                    </span>
                                @elseif($audit->event == 'deleted')
                                    <span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-red-100 text-red-800 dark:bg-red-900/20 dark:text-red-400">
                                        Deleted
                                    </span>
                                @else
                                    <span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-gray-100 text-gray-800 dark:bg-gray-900/20 dark:text-gray-400">
                                        {{ ucfirst($audit->event) }}
                                    </span>
                                @endif
                            </td>
                            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                                {{ class_basename($audit->auditable_type) }} #{{ $audit->auditable_id }}
                            </td>
                            <td class="px-6 py-4 text-sm text-gray-500 dark:text-gray-400">
                                @if($audit->event == 'created')
                                    <button type="button" onclick="showAuditDetails({{ $audit->id }}, 'new')" 
                                            class="text-indigo-600 dark:text-indigo-400 hover:text-indigo-900 dark:hover:text-indigo-300">
                                        View New Values
                                    </button>
                                @elseif($audit->event == 'updated')
                                    <button type="button" onclick="showAuditDetails({{ $audit->id }}, 'both')" 
                                            class="text-indigo-600 dark:text-indigo-400 hover:text-indigo-900 dark:hover:text-indigo-300">
                                        View Changes
                                    </button>
                                @elseif($audit->event == 'deleted')
                                    <button type="button" onclick="showAuditDetails({{ $audit->id }}, 'old')" 
                                            class="text-indigo-600 dark:text-indigo-400 hover:text-indigo-900 dark:hover:text-indigo-300">
                                        View Old Values
                                    </button>
                                @endif
                                <div id="audit-details-{{ $audit->id }}" class="hidden mt-2 p-2 bg-gray-50 dark:bg-gray-700 rounded text-xs">
                                    @if($audit->event == 'created')
                                        <div class="font-semibold mb-1 text-green-600 dark:text-green-400">New Values:</div>
                                        <pre class="whitespace-pre-wrap">{{ json_encode($audit->new_values, JSON_PRETTY_PRINT) }}</pre>
                                    @elseif($audit->event == 'updated')
                                        <div class="font-semibold mb-1 text-yellow-600 dark:text-yellow-400">Old Values:</div>
                                        <pre class="whitespace-pre-wrap mb-2">{{ json_encode($audit->old_values, JSON_PRETTY_PRINT) }}</pre>
                                        <div class="font-semibold mb-1 text-green-600 dark:text-green-400">New Values:</div>
                                        <pre class="whitespace-pre-wrap">{{ json_encode($audit->new_values, JSON_PRETTY_PRINT) }}</pre>
                                    @elseif($audit->event == 'deleted')
                                        <div class="font-semibold mb-1 text-red-600 dark:text-red-400">Deleted Values:</div>
                                        <pre class="whitespace-pre-wrap">{{ json_encode($audit->old_values, JSON_PRETTY_PRINT) }}</pre>
                                    @endif
                                </div>
                            </td>
                            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                                {{ $audit->ip_address ?? '-' }}
                            </td>
                        </tr>
                    @empty
                        <tr>
                            <td colspan="6" class="px-6 py-12 text-center">
                                <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                                </svg>
                                <h3 class="mt-2 text-sm font-medium text-gray-900 dark:text-white">No audit logs</h3>
                                <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">No activities have been recorded yet.</p>
                            </td>
                        </tr>
                    @endforelse
                </tbody>
            </table>
        </div>

        <!-- Pagination -->
        @if($audits->hasPages())
            <div class="bg-white dark:bg-gray-800 px-4 py-3 border-t border-gray-200 dark:border-gray-700 sm:px-6">
                {{ $audits->links() }}
            </div>
        @endif
    </div>
</div>

@push('scripts')
<script>
    function showAuditDetails(auditId, type) {
        const detailsDiv = document.getElementById(`audit-details-${auditId}`);
        detailsDiv.classList.toggle('hidden');
    }
</script>
@endpush
@endsection
