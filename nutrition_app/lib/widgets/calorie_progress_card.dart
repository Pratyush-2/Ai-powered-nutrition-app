import 'package:flutter/material.dart';

class CalorieProgressCard extends StatelessWidget {
  final double caloriesConsumed;
  final double caloriesGoal;

  const CalorieProgressCard({
    super.key,
    required this.caloriesConsumed,
    required this.caloriesGoal,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final progress = caloriesGoal > 0 ? (caloriesConsumed / caloriesGoal).clamp(0.0, 1.0) : 0.0;

    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Calories', style: theme.textTheme.titleMedium?.copyWith(fontWeight: FontWeight.bold)),
            const SizedBox(height: 8),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text('${caloriesConsumed.toInt()} / ${caloriesGoal.toInt()} kcal', style: theme.textTheme.bodyLarge),
                Text('${(progress * 100).toInt()}%', style: theme.textTheme.bodyLarge?.copyWith(fontWeight: FontWeight.bold)),
              ],
            ),
            const SizedBox(height: 8),
            LinearProgressIndicator(
              value: progress,
              minHeight: 10,
              borderRadius: BorderRadius.circular(5),
            ),
          ],
        ),
      ),
    );
  }
}