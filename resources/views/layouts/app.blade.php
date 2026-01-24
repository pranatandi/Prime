<!DOCTYPE html>
<html lang="{{ str_replace('_', '-', app()->getLocale()) }}" class="h-full">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta name="csrf-token" content="{{ csrf_token() }}">
    <meta name="theme-color" content="#4F46E5">
    
    <title>{{ config('app.name', 'Prime Weighing System') }} - @yield('title')</title>
    
    <!-- PWA Manifest -->
    <link rel="manifest" href="{{ asset('manifest.json') }}">
    <link rel="apple-touch-icon" href="{{ asset('images/icon-192x192.png') }}">
    
    <!-- Fonts -->
    <link rel="preconnect" href="https://fonts.bunny.net">
    <link href="https://fonts.bunny.net/css?family=inter:400,500,600,700" rel="stylesheet" />
    
    <!-- Styles -->
    @vite(['resources/css/app.css', 'resources/js/app.js'])
    
    @stack('styles')
</head>
<body class="h-full bg-gray-50 dark:bg-gray-900">
    <div class="min-h-full">
        <!-- Navigation -->
        <nav class="bg-indigo-600 dark:bg-indigo-800 shadow-lg">
            <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
                <div class="flex h-16 items-center justify-between">
                    <div class="flex items-center">
                        <div class="flex-shrink-0">
                            <h1 class="text-white text-xl font-bold">Prime Weighing</h1>
                        </div>
                        <div class="hidden md:block">
                            <div class="ml-10 flex items-baseline space-x-4">
                                <a href="{{ route('dashboard') }}" 
                                   class="@if(request()->routeIs('dashboard')) bg-indigo-700 dark:bg-indigo-900 @else hover:bg-indigo-500 dark:hover:bg-indigo-700 @endif text-white rounded-md px-3 py-2 text-sm font-medium">
                                    Dashboard
                                </a>
                                <a href="{{ route('weighing.index') }}" 
                                   class="@if(request()->routeIs('weighing.*')) bg-indigo-700 dark:bg-indigo-900 @else hover:bg-indigo-500 dark:hover:bg-indigo-700 @endif text-white rounded-md px-3 py-2 text-sm font-medium">
                                    Weighing
                                </a>
                                <a href="{{ route('suppliers.index') }}" 
                                   class="@if(request()->routeIs('suppliers.*')) bg-indigo-700 dark:bg-indigo-900 @else hover:bg-indigo-500 dark:hover:bg-indigo-700 @endif text-white rounded-md px-3 py-2 text-sm font-medium">
                                    Suppliers
                                </a>
                                <a href="{{ route('vehicles.index') }}" 
                                   class="@if(request()->routeIs('vehicles.*')) bg-indigo-700 dark:bg-indigo-900 @else hover:bg-indigo-500 dark:hover:bg-indigo-700 @endif text-white rounded-md px-3 py-2 text-sm font-medium">
                                    Vehicles
                                </a>
                                <a href="{{ route('audit-logs.index') }}" 
                                   class="@if(request()->routeIs('audit-logs.*')) bg-indigo-700 dark:bg-indigo-900 @else hover:bg-indigo-500 dark:hover:bg-indigo-700 @endif text-white rounded-md px-3 py-2 text-sm font-medium">
                                    Audit Logs
                                </a>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Mobile menu button -->
                    <div class="md:hidden">
                        <button type="button" id="mobile-menu-button" 
                                class="inline-flex items-center justify-center rounded-md bg-indigo-600 p-2 text-white hover:bg-indigo-500 focus:outline-none focus:ring-2 focus:ring-white focus:ring-offset-2 focus:ring-offset-indigo-600">
                            <span class="sr-only">Open main menu</span>
                            <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
                                <path stroke-linecap="round" stroke-linejoin="round" d="M3.75 6.75h16.5M3.75 12h16.5m-16.5 5.25h16.5" />
                            </svg>
                        </button>
                    </div>
                </div>
            </div>

            <!-- Mobile menu -->
            <div class="hidden md:hidden" id="mobile-menu">
                <div class="space-y-1 px-2 pb-3 pt-2 sm:px-3">
                    <a href="{{ route('dashboard') }}" class="@if(request()->routeIs('dashboard')) bg-indigo-700 @else hover:bg-indigo-500 @endif text-white block rounded-md px-3 py-2 text-base font-medium">Dashboard</a>
                    <a href="{{ route('weighing.index') }}" class="@if(request()->routeIs('weighing.*')) bg-indigo-700 @else hover:bg-indigo-500 @endif text-white block rounded-md px-3 py-2 text-base font-medium">Weighing</a>
                    <a href="{{ route('suppliers.index') }}" class="@if(request()->routeIs('suppliers.*')) bg-indigo-700 @else hover:bg-indigo-500 @endif text-white block rounded-md px-3 py-2 text-base font-medium">Suppliers</a>
                    <a href="{{ route('vehicles.index') }}" class="@if(request()->routeIs('vehicles.*')) bg-indigo-700 @else hover:bg-indigo-500 @endif text-white block rounded-md px-3 py-2 text-base font-medium">Vehicles</a>
                    <a href="{{ route('audit-logs.index') }}" class="@if(request()->routeIs('audit-logs.*')) bg-indigo-700 @else hover:bg-indigo-500 @endif text-white block rounded-md px-3 py-2 text-base font-medium">Audit Logs</a>
                </div>
            </div>
        </nav>

        <!-- Flash Messages -->
        @if(session('success'))
            <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 mt-4">
                <div class="rounded-md bg-green-50 dark:bg-green-900/20 p-4">
                    <div class="flex">
                        <div class="flex-shrink-0">
                            <svg class="h-5 w-5 text-green-400" viewBox="0 0 20 20" fill="currentColor">
                                <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.857-9.809a.75.75 0 00-1.214-.882l-3.483 4.79-1.88-1.88a.75.75 0 10-1.06 1.061l2.5 2.5a.75.75 0 001.137-.089l4-5.5z" clip-rule="evenodd" />
                            </svg>
                        </div>
                        <div class="ml-3">
                            <p class="text-sm font-medium text-green-800 dark:text-green-200">{{ session('success') }}</p>
                        </div>
                    </div>
                </div>
            </div>
        @endif

        @if(session('error'))
            <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 mt-4">
                <div class="rounded-md bg-red-50 dark:bg-red-900/20 p-4">
                    <div class="flex">
                        <div class="flex-shrink-0">
                            <svg class="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                                <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.28 7.22a.75.75 0 00-1.06 1.06L8.94 10l-1.72 1.72a.75.75 0 101.06 1.06L10 11.06l1.72 1.72a.75.75 0 101.06-1.06L11.06 10l1.72-1.72a.75.75 0 00-1.06-1.06L10 8.94 8.28 7.22z" clip-rule="evenodd" />
                            </svg>
                        </div>
                        <div class="ml-3">
                            <p class="text-sm font-medium text-red-800 dark:text-red-200">{{ session('error') }}</p>
                        </div>
                    </div>
                </div>
            </div>
        @endif

        <!-- Page Content -->
        <main>
            <div class="mx-auto max-w-7xl py-6 sm:px-6 lg:px-8">
                @yield('content')
            </div>
        </main>
    </div>

    <!-- PWA Install Prompt (optional) -->
    <div id="pwa-install-prompt" class="hidden fixed bottom-4 right-4 bg-white dark:bg-gray-800 shadow-lg rounded-lg p-4 max-w-sm">
        <p class="text-sm text-gray-700 dark:text-gray-300 mb-2">Install Prime Weighing for offline access!</p>
        <div class="flex gap-2">
            <button id="pwa-install-btn" class="bg-indigo-600 text-white px-3 py-1 rounded text-sm hover:bg-indigo-700">Install</button>
            <button id="pwa-dismiss-btn" class="bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 px-3 py-1 rounded text-sm hover:bg-gray-300 dark:hover:bg-gray-600">Dismiss</button>
        </div>
    </div>

    <!-- Scripts -->
    <script>
        // Mobile menu toggle
        document.getElementById('mobile-menu-button')?.addEventListener('click', function() {
            const menu = document.getElementById('mobile-menu');
            menu.classList.toggle('hidden');
        });
    </script>
    
    <!-- PWA Service Worker Registration -->
    <script src="{{ asset('js/pwa.js') }}"></script>
    
    @stack('scripts')
</body>
</html>
