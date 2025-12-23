import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:intl/intl.dart';
import 'package:nutrition_app/main.dart';
import 'package:nutrition_app/models/log.dart';
import 'package:nutrition_app/widgets/meal_card_with_recommendation.dart';

class HistoryScreen extends StatefulWidget {
  const HistoryScreen({super.key});

  @override
  State<HistoryScreen> createState() => _HistoryScreenState();
}

class _HistoryScreenState extends State<HistoryScreen> {
  late DateTime _selectedDate;
  late Future<List<DailyLogModel>> _dailyLogsFuture;

  @override
  void initState() {
    super.initState();
    _selectedDate = DateTime.now();
    _fetchLogs();
  }

  void _fetchLogs() {
    final formattedDate = DateFormat('yyyy-MM-dd').format(_selectedDate);
    setState(() {
      _dailyLogsFuture = apiService.getLogs(formattedDate);
    });
  }

  Future<void> _selectDate(BuildContext context) async {
    final DateTime? picked = await showDatePicker(
      context: context,
      initialDate: _selectedDate,
      firstDate: DateTime(2020),
      lastDate: DateTime(2030),
    );
    if (picked != null && picked != _selectedDate) {
      setState(() {
        _selectedDate = picked;
        _fetchLogs(); // Fetch logs for the newly selected date
      });
    }
  }

  Future<void> _copyDailyFoods(List<DailyLogModel> logs) async {
    if (logs.isEmpty) return;

    final dateStr = DateFormat('EEEE, MMMM d, yyyy').format(_selectedDate);
    final buffer = StringBuffer();
    buffer.writeln('📅 $dateStr\n');

    double totalCalories = 0;
    double totalProtein = 0;
    double totalCarbs = 0;
    double totalFats = 0;

    for (int i = 0; i < logs.length; i++) {
      final log = logs[i];
      final food = log.food;
      if (food == null) continue;

      // Calculate nutrition based on quantity (food values are per 100g)
      final multiplier = log.quantity / 100;
      final calories = food.calories * multiplier;
      final protein = food.protein * multiplier;
      final carbs = food.carbs * multiplier;
      final fats = food.fats * multiplier;

      buffer.writeln('${i + 1}. ${food.name}');
      buffer.writeln('   🔥 ${calories.toStringAsFixed(0)} kcal');
      buffer.writeln('   🥩 Protein: ${protein.toStringAsFixed(1)}g');
      buffer.writeln('   🍞 Carbs: ${carbs.toStringAsFixed(1)}g');
      buffer.writeln('   🧈 Fats: ${fats.toStringAsFixed(1)}g');
      buffer.writeln('   📏 Quantity: ${log.quantity.toStringAsFixed(0)}g\n');

      totalCalories += calories;
      totalProtein += protein;
      totalCarbs += carbs;
      totalFats += fats;
    }

    buffer.writeln('━━━━━━━━━━━━━━━━━━━━');
    buffer.writeln('📊 DAILY TOTALS:');
    buffer.writeln('🔥 Calories: ${totalCalories.toStringAsFixed(0)} kcal');
    buffer.writeln('🥩 Protein: ${totalProtein.toStringAsFixed(1)}g');
    buffer.writeln('🍞 Carbs: ${totalCarbs.toStringAsFixed(1)}g');
    buffer.writeln('🧈 Fats: ${totalFats.toStringAsFixed(1)}g');

    await Clipboard.setData(ClipboardData(text: buffer.toString()));
    
    if (!mounted) return;
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Row(
          children: [
            const Icon(Icons.check_circle, color: Colors.white),
            const SizedBox(width: 8),
            Text('Copied ${logs.length} food${logs.length > 1 ? 's' : ''} to clipboard!'),
          ],
        ),
        backgroundColor: Colors.green,
        duration: const Duration(seconds: 2),
      ),
    );
  }

  Future<void> _pasteDailyFoods() async {
    try {
      final clipboardData = await Clipboard.getData(Clipboard.kTextPlain);
      final text = clipboardData?.text;
      
      if (text == null || text.isEmpty) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Clipboard is empty'),
            backgroundColor: Colors.red,
          ),
        );
        return;
      }

      // Show confirmation dialog
      final confirmed = await showDialog<bool>(
        context: context,
        builder: (ctx) => AlertDialog(
          title: const Text('Paste Foods'),
          content: Text(
            'Paste foods to ${DateFormat('MMMM d, yyyy').format(_selectedDate)}?\n\n'
            'Note: This is a simplified paste. For best results, manually log foods.',
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(ctx, false),
              child: const Text('Cancel'),
            ),
            ElevatedButton(
              onPressed: () => Navigator.pop(ctx, true),
              child: const Text('Paste'),
            ),
          ],
        ),
      );

      if (confirmed != true) return;

      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Paste feature coming soon! For now, please log foods manually.'),
          backgroundColor: Colors.blue,
        ),
      );
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Error pasting: $e'),
          backgroundColor: Colors.red,
        ),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return SafeArea(
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('History', style: theme.textTheme.headlineSmall),
            const SizedBox(height: 12),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                GestureDetector(
                  onTap: () => _selectDate(context),
                  child: Row(
                    children: [
                      Icon(
                        Icons.calendar_today,
                        size: 18,
                        color: theme.colorScheme.primary,
                      ),
                      const SizedBox(width: 8),
                      Text(
                        DateFormat('EEEE, MMMM d').format(_selectedDate),
                        style: theme.textTheme.titleMedium?.copyWith(
                          color: theme.colorScheme.primary,
                        ),
                      ),
                      const Icon(Icons.arrow_drop_down, color: Colors.grey),
                    ],
                  ),
                ),
                // Ultra-compact icon buttons
                Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    // Paste button (icon only)
                    Tooltip(
                      message: 'Paste foods',
                      child: GestureDetector(
                        onTap: _pasteDailyFoods,
                        child: Container(
                          padding: const EdgeInsets.all(6),
                          decoration: BoxDecoration(
                            color: theme.colorScheme.secondary.withOpacity(0.1),
                            borderRadius: BorderRadius.circular(6),
                            border: Border.all(
                              color: theme.colorScheme.secondary,
                              width: 1,
                            ),
                          ),
                          child: Icon(
                            Icons.paste,
                            size: 16,
                            color: theme.colorScheme.secondary,
                          ),
                        ),
                      ),
                    ),
                    const SizedBox(width: 6),
                    // Copy button (icon only)
                    FutureBuilder<List<DailyLogModel>>(
                      future: _dailyLogsFuture,
                      builder: (context, snapshot) {
                        final hasLogs = snapshot.hasData && snapshot.data!.isNotEmpty;
                        return Tooltip(
                          message: hasLogs ? 'Copy foods' : 'No foods to copy',
                          child: GestureDetector(
                            onTap: hasLogs ? () => _copyDailyFoods(snapshot.data!) : null,
                            child: Container(
                              padding: const EdgeInsets.all(6),
                              decoration: BoxDecoration(
                                color: hasLogs 
                                    ? theme.colorScheme.primary.withOpacity(0.1)
                                    : Colors.grey.withOpacity(0.1),
                                borderRadius: BorderRadius.circular(6),
                                border: Border.all(
                                  color: hasLogs 
                                      ? theme.colorScheme.primary
                                      : Colors.grey,
                                  width: 1,
                                ),
                              ),
                              child: Icon(
                                Icons.copy,
                                size: 16,
                                color: hasLogs 
                                    ? theme.colorScheme.primary
                                    : Colors.grey,
                              ),
                            ),
                          ),
                        );
                      },
                    ),
                  ],
                ),
              ],
            ),
            const SizedBox(height: 16),
            Expanded(
              child: FutureBuilder<List<DailyLogModel>>(
                future: _dailyLogsFuture,
                builder: (context, snapshot) {
                  if (snapshot.connectionState == ConnectionState.waiting) {
                    return const Center(child: CircularProgressIndicator());
                  } else if (snapshot.hasError) {
                    return Center(
                      child: Text('Error loading logs: ${snapshot.error}'),
                    );
                  } else if (snapshot.hasData && snapshot.data!.isNotEmpty) {
                    final logs = snapshot.data!;
                    return ListView.builder(
                      itemCount: logs.length,
                      itemBuilder: (context, index) {
                        final log = logs[index];
                        final food = log.food;
                        if (food == null) return const SizedBox.shrink();
                        return MealCardWithRecommendation(
                          log: log,
                          onEdit: () {
                            // Placeholder for edit logic
                          },
                          onDelete: () {
                            // Placeholder for delete logic
                          },
                        );
                      },
                    );
                  } else {
                    return const Center(child: Text('No logs for this date.'));
                  }
                },
              ),
            ),
          ],
        ),
      ),
    );
  }
}
