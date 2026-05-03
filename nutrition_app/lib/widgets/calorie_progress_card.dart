import 'package:flutter/material.dart';
import 'package:nutrition_app/theme/app_theme.dart';
import 'package:nutrition_app/widgets/glass_card.dart';

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
    final progress = caloriesGoal > 0 ? (caloriesConsumed / caloriesGoal).clamp(0.0, 1.0) : 0.0;

    return GlassCard(
      child: Column(
        children: [
          const Text(
            'Daily Calories',
            style: TextStyle(
              fontSize: 18,
              fontWeight: FontWeight.bold,
              color: AppTheme.textPrimary,
            ),
          ),
          const SizedBox(height: 24),
          Stack(
            alignment: Alignment.center,
            children: [
              SizedBox(
                width: 150,
                height: 150,
                child: CircularProgressIndicator(
                  value: progress,
                  strokeWidth: 12,
                  backgroundColor: AppTheme.surface,
                  valueColor: const AlwaysStoppedAnimation<Color>(AppTheme.primary),
                  strokeCap: StrokeCap.round,
                ),
              ),
              Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Text(
                    '${caloriesConsumed.toInt()}',
                    style: const TextStyle(
                      fontSize: 32,
                      fontWeight: FontWeight.bold,
                      color: AppTheme.primary,
                    ),
                  ),
                  Text(
                    '/ ${caloriesGoal.toInt()} kcal',
                    style: const TextStyle(
                      fontSize: 14,
                      color: AppTheme.textSecondary,
                    ),
                  ),
                ],
              ),
            ],
          ),
          const SizedBox(height: 16),
          Text(
            '${(progress * 100).toInt()}% of daily goal',
            style: const TextStyle(color: AppTheme.textSecondary),
          ),
        ],
      ),
    );
  }
}