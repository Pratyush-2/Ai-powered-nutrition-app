import 'package:flutter/material.dart';
import 'package:nutrition_app/main.dart';
import 'package:fl_chart/fl_chart.dart';
import 'package:intl/intl.dart';
import '../models/goal.dart';
import 'dart:developer' as developer;

class GoalsScreen extends StatefulWidget {
  final VoidCallback? onGoalsUpdated;
  final bool isGuest;
  const GoalsScreen({super.key, this.onGoalsUpdated, this.isGuest = false});

  @override
  State<GoalsScreen> createState() => _GoalsScreenState();
}

class _GoalsScreenState extends State<GoalsScreen> {
  late Future<List<Goal>> _goalsFuture;
  late Future<List<Map<String, dynamic>>> _weekDataFuture;
  bool _saving = false;
  
  // Chart selection
  String _selectedMetric = 'calories'; // calories, protein, carbs, fats

  @override
  void initState() {
    super.initState();
    _fetch();
  }

  void _fetch() {
    setState(() {
      _goalsFuture = apiService.getGoals();
      _weekDataFuture = _fetchWeekData();
    });
  }

  Future<List<Map<String, dynamic>>> _fetchWeekData() async {
    final List<Map<String, dynamic>> weekData = [];
    final now = DateTime.now();
    
    for (int i = 6; i >= 0; i--) {
      final date = now.subtract(Duration(days: i));
      final dateStr = DateFormat('yyyy-MM-dd').format(date);
      
      try {
        final totals = await apiService.getTotals(dateStr);
        weekData.add({
          'date': date,
          'dateStr': dateStr,
          'calories': totals['calories'] ?? 0.0,
          'protein': totals['protein'] ?? 0.0,
          'carbs': totals['carbs'] ?? 0.0,
          'fats': totals['fats'] ?? 0.0,
        });
      } catch (e) {
        developer.log('Error fetching data for $dateStr: $e');
        weekData.add({
          'date': date,
          'dateStr': dateStr,
          'calories': 0.0,
          'protein': 0.0,
          'carbs': 0.0,
          'fats': 0.0,
        });
      }
    }
    
    return weekData;
  }

  void _showSnack(String message) {
    if (!mounted) return;
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text(message)),
    );
  }

  Future<void> _editGoals(Goal current) async {
    final caloriesCtrl = TextEditingController(
      text: current.caloriesGoal.toString(),
    );
    final proteinCtrl = TextEditingController(
      text: current.proteinGoal.toString(),
    );
    final carbsCtrl = TextEditingController(text: current.carbsGoal.toString());
    final fatsCtrl = TextEditingController(text: current.fatsGoal.toString());

    await showDialog(
      context: context,
      builder: (ctx) {
        return AlertDialog(
          title: const Text('Edit Goals'),
          content: SingleChildScrollView(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                TextField(
                  controller: caloriesCtrl,
                  keyboardType: TextInputType.number,
                  decoration: const InputDecoration(labelText: 'Calories Goal'),
                ),
                const SizedBox(height: 12),
                TextField(
                  controller: proteinCtrl,
                  keyboardType: TextInputType.number,
                  decoration: const InputDecoration(labelText: 'Protein Goal (g)'),
                ),
                const SizedBox(height: 12),
                TextField(
                  controller: carbsCtrl,
                  keyboardType: TextInputType.number,
                  decoration: const InputDecoration(labelText: 'Carbs Goal (g)'),
                ),
                const SizedBox(height: 12),
                TextField(
                  controller: fatsCtrl,
                  keyboardType: TextInputType.number,
                  decoration: const InputDecoration(labelText: 'Fats Goal (g)'),
                ),
              ],
            ),
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(ctx),
              child: const Text('Cancel'),
            ),
            ElevatedButton(
              onPressed: () async {
                Navigator.pop(ctx);
                setState(() => _saving = true);
                try {
                  final updated = current.copyWith(
                    caloriesGoal: double.tryParse(caloriesCtrl.text) ?? current.caloriesGoal,
                    proteinGoal: double.tryParse(proteinCtrl.text) ?? current.proteinGoal,
                    carbsGoal: double.tryParse(carbsCtrl.text) ?? current.carbsGoal,
                    fatsGoal: double.tryParse(fatsCtrl.text) ?? current.fatsGoal,
                  );
                  await apiService.updateGoals(updated);
                  _showSnack('Goals updated successfully!');
                  _fetch();
                  widget.onGoalsUpdated?.call();
                } catch (e) {
                  _showSnack('Failed to update goals: $e');
                } finally {
                  setState(() => _saving = false);
                }
              },
              child: const Text('Save'),
            ),
          ],
        );
      },
    );
  }

  Widget _buildMetricSelector() {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
      child: Row(
        children: [
          _buildMetricChip('Calories', 'calories', Colors.orange),
          const SizedBox(width: 8),
          _buildMetricChip('Protein', 'protein', Colors.red),
          const SizedBox(width: 8),
          _buildMetricChip('Carbs', 'carbs', Colors.blue),
          const SizedBox(width: 8),
          _buildMetricChip('Fats', 'fats', Colors.purple),
        ],
      ),
    );
  }

  Widget _buildMetricChip(String label, String value, Color color) {
    final isSelected = _selectedMetric == value;
    return Expanded(
      child: GestureDetector(
        onTap: () => setState(() => _selectedMetric = value),
        child: AnimatedContainer(
          duration: const Duration(milliseconds: 200),
          padding: const EdgeInsets.symmetric(vertical: 12),
          decoration: BoxDecoration(
            color: isSelected ? color : color.withOpacity(0.1),
            borderRadius: BorderRadius.circular(12),
            border: Border.all(
              color: color,
              width: isSelected ? 2 : 1,
            ),
          ),
          child: Text(
            label,
            textAlign: TextAlign.center,
            style: TextStyle(
              color: isSelected ? Colors.white : color,
              fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
              fontSize: 12,
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildChart(List<Map<String, dynamic>> weekData, Goal? goal) {
    final spots = <FlSpot>[];
    double maxY = 100;
    double goalValue = 0;

    // Get data based on selected metric
    for (int i = 0; i < weekData.length; i++) {
      final value = weekData[i][_selectedMetric] as double;
      spots.add(FlSpot(i.toDouble(), value));
      if (value > maxY) maxY = value;
    }

    // Get goal value for the selected metric
    if (goal != null) {
      switch (_selectedMetric) {
        case 'calories':
          goalValue = goal.caloriesGoal;
          break;
        case 'protein':
          goalValue = goal.proteinGoal;
          break;
        case 'carbs':
          goalValue = goal.carbsGoal;
          break;
        case 'fats':
          goalValue = goal.fatsGoal;
          break;
      }
      if (goalValue > maxY) maxY = goalValue;
    }

    // Add some padding to maxY
    maxY = maxY * 1.2;

    final metricColor = _getMetricColor();

    return Container(
      height: 280,
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: [
            metricColor.withOpacity(0.05),
            metricColor.withOpacity(0.02),
          ],
        ),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: metricColor.withOpacity(0.2)),
      ),
      child: LineChart(
        LineChartData(
          gridData: FlGridData(
            show: true,
            drawVerticalLine: false,
            horizontalInterval: maxY / 5,
            getDrawingHorizontalLine: (value) {
              return FlLine(
                color: Colors.grey.withOpacity(0.2),
                strokeWidth: 1,
              );
            },
          ),
          titlesData: FlTitlesData(
            show: true,
            rightTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)),
            topTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)),
            bottomTitles: AxisTitles(
              sideTitles: SideTitles(
                showTitles: true,
                reservedSize: 30,
                interval: 1,
                getTitlesWidget: (value, meta) {
                  if (value.toInt() >= 0 && value.toInt() < weekData.length) {
                    final date = weekData[value.toInt()]['date'] as DateTime;
                    return Padding(
                      padding: const EdgeInsets.only(top: 8.0),
                      child: Text(
                        DateFormat('E').format(date).substring(0, 1),
                        style: TextStyle(
                          color: Colors.grey[600],
                          fontWeight: FontWeight.bold,
                          fontSize: 12,
                        ),
                      ),
                    );
                  }
                  return const Text('');
                },
              ),
            ),
            leftTitles: AxisTitles(
              sideTitles: SideTitles(
                showTitles: true,
                interval: maxY / 5,
                reservedSize: 42,
                getTitlesWidget: (value, meta) {
                  return Text(
                    value.toInt().toString(),
                    style: TextStyle(
                      color: Colors.grey[600],
                      fontWeight: FontWeight.bold,
                      fontSize: 10,
                    ),
                  );
                },
              ),
            ),
          ),
          borderData: FlBorderData(show: false),
          minX: 0,
          maxX: 6,
          minY: 0,
          maxY: maxY,
          lineBarsData: [
            LineChartBarData(
              spots: spots,
              isCurved: true,
              gradient: LinearGradient(
                colors: [metricColor.withOpacity(0.8), metricColor],
              ),
              barWidth: 4,
              isStrokeCapRound: true,
              dotData: FlDotData(
                show: true,
                getDotPainter: (spot, percent, barData, index) {
                  return FlDotCirclePainter(
                    radius: 6,
                    color: metricColor,
                    strokeWidth: 2,
                    strokeColor: Colors.white,
                  );
                },
              ),
              belowBarData: BarAreaData(
                show: true,
                gradient: LinearGradient(
                  colors: [
                    metricColor.withOpacity(0.3),
                    metricColor.withOpacity(0.0),
                  ],
                  begin: Alignment.topCenter,
                  end: Alignment.bottomCenter,
                ),
              ),
            ),
          ],
          extraLinesData: ExtraLinesData(
            horizontalLines: goalValue > 0
                ? [
                    HorizontalLine(
                      y: goalValue,
                      color: metricColor.withOpacity(0.5),
                      strokeWidth: 2,
                      dashArray: [5, 5],
                      label: HorizontalLineLabel(
                        show: true,
                        alignment: Alignment.topRight,
                        padding: const EdgeInsets.only(right: 5, bottom: 5),
                        style: TextStyle(
                          color: metricColor,
                          fontWeight: FontWeight.bold,
                          fontSize: 12,
                        ),
                        labelResolver: (line) => 'Goal',
                      ),
                    ),
                  ]
                : [],
          ),
        ),
      ),
    );
  }

  Color _getMetricColor() {
    switch (_selectedMetric) {
      case 'calories':
        return Colors.orange;
      case 'protein':
        return Colors.red;
      case 'carbs':
        return Colors.blue;
      case 'fats':
        return Colors.purple;
      default:
        return Colors.orange;
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Goals & Progress'),
        elevation: 0,
      ),
      body: FutureBuilder<List<Goal>>(
        future: _goalsFuture,
        builder: (context, snapshot) {
          if (snapshot.connectionState == ConnectionState.waiting) {
            return const Center(child: CircularProgressIndicator());
          }

          if (snapshot.hasError) {
            return Center(child: Text('Error: ${snapshot.error}'));
          }

          final goals = snapshot.data ?? [];
          final goal = goals.isNotEmpty ? goals.first : null;

          return SingleChildScrollView(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // Progress Chart Section
                Text(
                  'Weekly Progress',
                  style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                        fontWeight: FontWeight.bold,
                      ),
                ),
                const SizedBox(height: 16),
                _buildMetricSelector(),
                const SizedBox(height: 16),
                FutureBuilder<List<Map<String, dynamic>>>(
                  future: _weekDataFuture,
                  builder: (context, weekSnapshot) {
                    if (weekSnapshot.connectionState == ConnectionState.waiting) {
                      return Container(
                        height: 280,
                        alignment: Alignment.center,
                        child: const CircularProgressIndicator(),
                      );
                    }

                    if (weekSnapshot.hasError) {
                      return Container(
                        height: 280,
                        alignment: Alignment.center,
                        child: Text('Error loading chart data'),
                      );
                    }

                    final weekData = weekSnapshot.data ?? [];
                    return _buildChart(weekData, goal);
                  },
                ),
                const SizedBox(height: 32),

                // Goals Section
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text(
                      'Your Goals',
                      style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                            fontWeight: FontWeight.bold,
                          ),
                    ),
                    if (goal != null)
                      IconButton(
                        icon: const Icon(Icons.edit),
                        onPressed: _saving ? null : () => _editGoals(goal),
                      ),
                  ],
                ),
                const SizedBox(height: 16),

                if (goal == null)
                  const Center(
                    child: Padding(
                      padding: EdgeInsets.all(32.0),
                      child: Text('No goals set yet'),
                    ),
                  )
                else
                  Column(
                    children: [
                      _buildGoalCard('Calories', goal.caloriesGoal, 'kcal', Colors.orange),
                      const SizedBox(height: 12),
                      _buildGoalCard('Protein', goal.proteinGoal, 'g', Colors.red),
                      const SizedBox(height: 12),
                      _buildGoalCard('Carbs', goal.carbsGoal, 'g', Colors.blue),
                      const SizedBox(height: 12),
                      _buildGoalCard('Fats', goal.fatsGoal, 'g', Colors.purple),
                    ],
                  ),
              ],
            ),
          );
        },
      ),
    );
  }

  Widget _buildGoalCard(String label, double value, String unit, Color color) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: [
            color.withOpacity(0.1),
            color.withOpacity(0.05),
          ],
        ),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: color.withOpacity(0.3)),
      ),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(
            label,
            style: TextStyle(
              fontSize: 16,
              fontWeight: FontWeight.w600,
              color: color,
            ),
          ),
          Text(
            '${value.toStringAsFixed(0)} $unit',
            style: TextStyle(
              fontSize: 20,
              fontWeight: FontWeight.bold,
              color: color,
            ),
          ),
        ],
      ),
    );
  }
}
