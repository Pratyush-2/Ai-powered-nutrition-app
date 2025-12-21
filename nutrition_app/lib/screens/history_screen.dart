import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
// import 'package:nutrition_app/widgets/meal_card.dart';
import 'package:nutrition_app/services/api_client.dart'; // Import the centralized API client
import 'package:nutrition_app/models/log.dart';
import 'package:nutrition_app/widgets/meal_card_with_recommendation.dart';

class HistoryScreen extends StatefulWidget {
  final int userId;
  const HistoryScreen({super.key, required this.userId});

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
      _dailyLogsFuture = apiService.getLogs(widget.userId, formattedDate);
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
                          userId: widget.userId,
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
