import 'package:flutter/material.dart';

class MacroSummary extends StatelessWidget {
  final String title;
  final int currentValue;
  final int goalValue;
  final Color color;

  const MacroSummary({
    super.key,
    required this.title,
    required this.currentValue,
    required this.goalValue,
    required this.color,
  });

  @override
  Widget build(BuildContext context) {
    double progress =
        goalValue > 0 ? (currentValue / goalValue).clamp(0, 1).toDouble() : 0.0;

    return Expanded(
      child: Card(
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
        child: Padding(
          padding: const EdgeInsets.all(12.0),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.start,
            children: [
              Text(
                title,
                style: Theme.of(context).textTheme.titleMedium,
              ),
              const SizedBox(height: 12),
              SizedBox(
                height: 60,
                width: 60,
                child: Stack(
                  fit: StackFit.expand,
                  children: [
                    CircularProgressIndicator(
                      value: progress,
                      backgroundColor: Theme.of(context).colorScheme.surfaceContainerHighest,
                      color: color,
                      strokeWidth: 6,
                    ),
                    Center(
                      child: Text(
                        '$currentValue',
                        style: Theme.of(context).textTheme.titleMedium?.copyWith(fontWeight: FontWeight.w800),
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 8),
              Text(
                "/ $goalValue",
                style: Theme.of(context).textTheme.bodySmall,
              ),
            ],
          ),
        ),
      ),
    );
  }
}
