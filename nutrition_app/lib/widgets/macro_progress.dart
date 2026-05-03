import 'package:flutter/material.dart';
import 'package:nutrition_app/theme/app_theme.dart';

class MacroProgress extends StatelessWidget {
  final String label;
  final double current;
  final double goal;

  const MacroProgress({
    super.key,
    required this.label,
    required this.current,
    required this.goal,
  });

  @override
  Widget build(BuildContext context) {
    final percent = goal > 0 ? (current / goal).clamp(0.0, 1.0) : 0.0;

    Color progressColor;
    if (label.toLowerCase().contains('protein')) {
      progressColor = AppTheme.primary;
    } else if (label.toLowerCase().contains('carbs')) {
      progressColor = AppTheme.secondary;
    } else if (label.toLowerCase().contains('fats')) {
      progressColor = AppTheme.accent;
    } else {
      progressColor = AppTheme.primary;
    }

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text(label, style: const TextStyle(fontWeight: FontWeight.bold, color: AppTheme.textPrimary)),
            Text('${current.toInt()}g / ${goal.toInt()}g', style: const TextStyle(color: AppTheme.textSecondary)),
          ],
        ),
        const SizedBox(height: 8),
        Container(
          height: 8,
          decoration: BoxDecoration(
            borderRadius: BorderRadius.circular(4),
            color: AppTheme.surface,
            boxShadow: [
              BoxShadow(
                color: progressColor.withOpacity(0.2),
                blurRadius: 4,
                offset: const Offset(0, 2),
              ),
            ],
          ),
          child: ClipRRect(
            borderRadius: BorderRadius.circular(4),
            child: LinearProgressIndicator(
              value: percent,
              backgroundColor: Colors.transparent,
              valueColor: AlwaysStoppedAnimation<Color>(progressColor),
            ),
          ),
        ),
      ],
    );
  }
}