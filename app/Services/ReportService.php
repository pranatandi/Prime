<?php

namespace App\Services;

use App\Models\Weighing;
use Carbon\Carbon;
use Illuminate\Support\Facades\DB;

/**
 * Report Service for generating statistics and reports
 */
class ReportService
{
    /**
     * Get daily statistics
     * 
     * @param string|null $date
     * @return array
     */
    public function getDailyStats(?string $date = null): array
    {
        $date = $date ?? Carbon::today()->toDateString();
        
        $stats = Weighing::whereDate('weighing_datetime', $date)
            ->select(
                DB::raw('COUNT(*) as total_transactions'),
                DB::raw('SUM(net_weight) as total_weight'),
                DB::raw('COUNT(DISTINCT vehicle_id) as total_vehicles'),
                DB::raw('COUNT(DISTINCT supplier_id) as total_suppliers')
            )
            ->first();

        return [
            'date' => $date,
            'total_transactions' => $stats->total_transactions ?? 0,
            'total_weight' => number_format($stats->total_weight ?? 0, 2),
            'total_vehicles' => $stats->total_vehicles ?? 0,
            'total_suppliers' => $stats->total_suppliers ?? 0,
        ];
    }

    /**
     * Get monthly statistics
     * 
     * @param int $year
     * @param int $month
     * @return array
     */
    public function getMonthlyStats(int $year, int $month): array
    {
        $startDate = Carbon::createFromDate($year, $month, 1)->startOfMonth();
        $endDate = Carbon::createFromDate($year, $month, 1)->endOfMonth();

        $stats = Weighing::whereBetween('weighing_datetime', [$startDate, $endDate])
            ->select(
                DB::raw('COUNT(*) as total_transactions'),
                DB::raw('SUM(net_weight) as total_weight'),
                DB::raw('COUNT(DISTINCT vehicle_id) as total_vehicles')
            )
            ->first();

        return [
            'period' => $startDate->format('F Y'),
            'total_transactions' => $stats->total_transactions ?? 0,
            'total_weight' => number_format($stats->total_weight ?? 0, 2),
            'total_vehicles' => $stats->total_vehicles ?? 0,
        ];
    }

    /**
     * Get weighing chart data for a period
     * 
     * @param string $startDate
     * @param string $endDate
     * @return array
     */
    public function getChartData(string $startDate, string $endDate): array
    {
        $data = Weighing::whereBetween('weighing_datetime', [$startDate, $endDate])
            ->select(
                DB::raw('DATE(weighing_datetime) as date'),
                DB::raw('SUM(net_weight) as total_weight'),
                DB::raw('COUNT(*) as transactions')
            )
            ->groupBy('date')
            ->orderBy('date')
            ->get();

        return [
            'labels' => $data->pluck('date')->toArray(),
            'weights' => $data->pluck('total_weight')->toArray(),
            'transactions' => $data->pluck('transactions')->toArray(),
        ];
    }

    /**
     * Get top suppliers by weight
     * 
     * @param int $limit
     * @return \Illuminate\Support\Collection
     */
    public function getTopSuppliers(int $limit = 10)
    {
        return Weighing::with('supplier')
            ->select('supplier_id', DB::raw('SUM(net_weight) as total_weight'))
            ->groupBy('supplier_id')
            ->orderByDesc('total_weight')
            ->limit($limit)
            ->get();
    }
}
