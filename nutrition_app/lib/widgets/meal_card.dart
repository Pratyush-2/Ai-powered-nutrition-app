import 'package:flutter/material.dart';
import 'package:nutrition_app/theme/app_theme.dart';
import 'package:nutrition_app/widgets/glass_card.dart';

class MealCard extends StatelessWidget {
  final String title;
  final int kcal;
  final String time;
  final IconData icon;
  final String recommendation;
  final VoidCallback? onEdit;
  final VoidCallback? onDelete;
  final VoidCallback? onChat;

  const MealCard({
    super.key,
    required this.title,
    required this.kcal,
    required this.time,
    required this.icon,
    required this.recommendation,
    this.onEdit,
    this.onDelete,
    this.onChat,
  });

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 16.0, vertical: 8.0),
      child: GlassCard(
        padding: const EdgeInsets.all(0), // ListTile handles padding
        child: ListTile(
          contentPadding:
              const EdgeInsets.symmetric(vertical: 12.0, horizontal: 16.0),
          leading: Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: AppTheme.primary.withOpacity(0.1),
              shape: BoxShape.circle,
            ),
            child: Icon(icon, color: AppTheme.primary),
          ),
          title: Text(
            title, 
            style: const TextStyle(
              fontSize: 18, 
              fontWeight: FontWeight.bold, 
              color: AppTheme.textPrimary
            )
          ),
          subtitle: Padding(
            padding: const EdgeInsets.only(top: 8.0),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  '$kcal kcal  •  $time', 
                  style: const TextStyle(
                    color: AppTheme.primary, 
                    fontWeight: FontWeight.w600
                  )
                ),
                const SizedBox(height: 4),
                Text(
                  'AI: $recommendation', 
                  style: const TextStyle(color: AppTheme.textSecondary)
                ),
              ],
            ),
          ),
          trailing: PopupMenuButton<String>(
            icon: const Icon(Icons.more_vert, color: AppTheme.textSecondary),
            color: AppTheme.surface,
            onSelected: (value) {
              if (value == 'edit') {
                onEdit?.call();
              } else if (value == 'delete') {
                onDelete?.call();
              } else if (value == 'chat') {
                onChat?.call();
              }
            },
            itemBuilder: (BuildContext context) => <PopupMenuEntry<String>>[
              const PopupMenuItem<String>(
                value: 'chat',
                child: Text('Chat about this food', style: TextStyle(color: AppTheme.textPrimary)),
              ),
              const PopupMenuItem<String>(
                value: 'edit',
                child: Text('Edit', style: TextStyle(color: AppTheme.textPrimary)),
              ),
              const PopupMenuItem<String>(
                value: 'delete',
                child: Text('Delete', style: TextStyle(color: AppTheme.error)),
              ),
            ],
          ),
        ),
      ),
    );
  }
}