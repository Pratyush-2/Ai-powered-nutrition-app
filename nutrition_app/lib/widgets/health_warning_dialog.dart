import 'package:flutter/material.dart';
import 'package:nutrition_app/models/health_profile.dart';

class HealthWarningDialog extends StatelessWidget {
  final List<HealthWarning> warnings;
  final String foodName;
  final VoidCallback onProceed;
  final VoidCallback onCancel;

  const HealthWarningDialog({
    super.key,
    required this.warnings,
    required this.foodName,
    required this.onProceed,
    required this.onCancel,
  });

  @override
  Widget build(BuildContext context) {
    final criticalWarnings = warnings.where((w) => w.isCritical).toList();
    final otherWarnings = warnings.where((w) => !w.isCritical).toList();
    
    return AlertDialog(
      title: Row(
        children: [
          Icon(
            criticalWarnings.isNotEmpty ? Icons.error : Icons.warning,
            color: criticalWarnings.isNotEmpty ? Colors.red : Colors.orange,
            size: 28,
          ),
          const SizedBox(width: 8),
          const Expanded(
            child: Text('Health Warning'),
          ),
        ],
      ),
      content: SingleChildScrollView(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'This food may not be suitable for you:',
              style: const TextStyle(fontWeight: FontWeight.w500),
            ),
            const SizedBox(height: 12),
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: Colors.grey.shade100,
                borderRadius: BorderRadius.circular(8),
              ),
              child: Row(
                children: [
                  const Icon(Icons.restaurant, size: 20),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      foodName,
                      style: const TextStyle(
                        fontWeight: FontWeight.bold,
                        fontSize: 16,
                      ),
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 16),
            
            // Critical warnings
            if (criticalWarnings.isNotEmpty) ...[
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: Colors.red.shade50,
                  border: Border.all(color: Colors.red.shade200),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        Icon(Icons.error, color: Colors.red.shade700, size: 20),
                        const SizedBox(width: 8),
                        Text(
                          'CRITICAL ALERTS',
                          style: TextStyle(
                            color: Colors.red.shade700,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 8),
                    ...criticalWarnings.map((warning) => Padding(
                      padding: const EdgeInsets.only(bottom: 4),
                      child: Row(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(warning.icon, style: const TextStyle(fontSize: 16)),
                          const SizedBox(width: 8),
                          Expanded(
                            child: Text(
                              warning.message,
                              style: TextStyle(color: Colors.red.shade900),
                            ),
                          ),
                        ],
                      ),
                    )),
                  ],
                ),
              ),
              const SizedBox(height: 12),
            ],
            
            // Other warnings
            if (otherWarnings.isNotEmpty) ...[
              ...otherWarnings.map((warning) => Padding(
                padding: const EdgeInsets.only(bottom: 8),
                child: Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: _getWarningColor(warning.severity).withOpacity(0.1),
                    border: Border.all(
                      color: _getWarningColor(warning.severity).withOpacity(0.3),
                    ),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Row(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(warning.icon, style: const TextStyle(fontSize: 18)),
                      const SizedBox(width: 8),
                      Expanded(
                        child: Text(
                          warning.message,
                          style: TextStyle(
                            color: _getWarningColor(warning.severity).shade900,
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
              )),
            ],
          ],
        ),
      ),
      actions: [
        TextButton(
          onPressed: onCancel,
          child: const Text('Cancel'),
        ),
        ElevatedButton(
          onPressed: onProceed,
          style: ElevatedButton.styleFrom(
            backgroundColor: criticalWarnings.isNotEmpty 
                ? Colors.red 
                : Colors.orange,
          ),
          child: Text(
            criticalWarnings.isNotEmpty ? 'Log Anyway' : 'Proceed',
          ),
        ),
      ],
    );
  }

  MaterialColor _getWarningColor(String severity) {
    switch (severity) {
      case 'critical':
        return Colors.red;
      case 'warning':
        return Colors.orange;
      case 'info':
        return Colors.blue;
      default:
        return Colors.grey;
    }
  }
}

class WarningBadge extends StatelessWidget {
  final List<HealthWarning> warnings;
  final VoidCallback? onTap;

  const WarningBadge({
    super.key,
    required this.warnings,
    this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    if (warnings.isEmpty) return const SizedBox.shrink();
    
    final criticalCount = warnings.where((w) => w.isCritical).length;
    final warningCount = warnings.where((w) => w.isWarning).length;
    
    return InkWell(
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
        decoration: BoxDecoration(
          color: criticalCount > 0 ? Colors.red.shade50 : Colors.orange.shade50,
          borderRadius: BorderRadius.circular(12),
          border: Border.all(
            color: criticalCount > 0 ? Colors.red.shade200 : Colors.orange.shade200,
          ),
        ),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(
              criticalCount > 0 ? Icons.error : Icons.warning,
              size: 16,
              color: criticalCount > 0 ? Colors.red.shade700 : Colors.orange.shade700,
            ),
            const SizedBox(width: 4),
            Text(
              '${warnings.length}',
              style: TextStyle(
                fontSize: 12,
                fontWeight: FontWeight.bold,
                color: criticalCount > 0 ? Colors.red.shade700 : Colors.orange.shade700,
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class WarningsList extends StatelessWidget {
  final List<HealthWarning> warnings;

  const WarningsList({
    super.key,
    required this.warnings,
  });

  @override
  Widget build(BuildContext context) {
    if (warnings.isEmpty) return const SizedBox.shrink();
    
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: warnings.map((warning) {
        return Padding(
          padding: const EdgeInsets.only(bottom: 4),
          child: Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(warning.icon, style: const TextStyle(fontSize: 14)),
              const SizedBox(width: 6),
              Expanded(
                child: Text(
                  warning.message,
                  style: TextStyle(
                    fontSize: 12,
                    color: _getTextColor(warning.severity),
                  ),
                ),
              ),
            ],
          ),
        );
      }).toList(),
    );
  }

  Color _getTextColor(String severity) {
    switch (severity) {
      case 'critical':
        return Colors.red.shade700;
      case 'warning':
        return Colors.orange.shade700;
      case 'info':
        return Colors.blue.shade700;
      default:
        return Colors.grey.shade700;
    }
  }
}
