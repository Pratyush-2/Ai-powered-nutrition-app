import 'package:flutter/material.dart';

class MealCard extends StatelessWidget {
  final String title;
  final int kcal;
  final String time;
  final IconData icon;
  final String recommendation;
  final VoidCallback? onEdit;
  final VoidCallback? onDelete;

  const MealCard({
    super.key,
    required this.title,
    required this.kcal,
    required this.time,
    required this.icon,
    required this.recommendation,
    this.onEdit,
    this.onDelete,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4.0),
      child: Card(
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
        child: ListTile(
          contentPadding:
              const EdgeInsets.symmetric(vertical: 8.0, horizontal: 16.0),
          leading: Icon(icon, color: theme.colorScheme.primary),
          title: Text(title, style: theme.textTheme.titleMedium),
          subtitle: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text('$kcal kcal  •  $time', style: theme.textTheme.bodyMedium),
              Text('Recommendation: $recommendation', style: theme.textTheme.bodySmall),
            ],
          ),
          trailing: PopupMenuButton<String>(
            onSelected: (value) {
              if (value == 'edit') {
                onEdit?.call();
              } else if (value == 'delete') {
                onDelete?.call();
              }
            },
            itemBuilder: (BuildContext context) => <PopupMenuEntry<String>>[
              const PopupMenuItem<String>(
                value: 'edit',
                child: Text('Edit'),
              ),
              const PopupMenuItem<String>(
                value: 'delete',
                child: Text('Delete'),
              ),
            ],
          ),
        ),
      ),
    );
  }
}