<?php

namespace App\Http\Controllers;

use App\Services\ReportService;
use Carbon\Carbon;
use Illuminate\Http\Request;

class DashboardController extends Controller
{
    protected $reportService;

    /**
     * Create a new controller instance.
     *
     * @param ReportService $reportService
     */
    public function __construct(ReportService $reportService)
    {
        $this->reportService = $reportService;
    }

    /**
     * Display the dashboard with statistics and charts.
     *
     * @return \Illuminate\View\View
     */
    public function index()
    {
        // Get daily statistics for today
        $dailyStats = $this->reportService->getDailyStats();

        // Get chart data for the last 7 days
        $endDate = Carbon::today()->toDateString();
        $startDate = Carbon::today()->subDays(6)->toDateString();
        $chartData = $this->reportService->getChartData($startDate, $endDate);

        // Get top 5 suppliers by weight
        $topSuppliers = $this->reportService->getTopSuppliers(5);

        return view('dashboard.index', compact('dailyStats', 'chartData', 'topSuppliers'));
    }
}
