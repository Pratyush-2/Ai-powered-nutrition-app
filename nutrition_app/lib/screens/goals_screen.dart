import 'package:flutter/material.dart';
import 'package:nutrition_app/services/api_client.dart';
import '../models/goal.dart';
import 'dart:developer' as developer;

class GoalsScreen extends StatefulWidget {
  final VoidCallback? onGoalsUpdated;
  const GoalsScreen({super.key, this.onGoalsUpdated});

  @override
  State<GoalsScreen> createState() => _GoalsScreenState();
}

class _GoalsScreenState extends State<GoalsScreen> {
  late Future<List<Map<String, dynamic>>> _goalsFuture;
  bool _saving = false;

  @override
  void initState() {
    super.initState();
    _fetch();
  }

  void _fetch() {
    setState(() {
      _goalsFuture = apiService.getAllGoals();
    });
  }

  void _showSnack(String message) {
    if (!mounted) return;
    ScaffoldMessenger.of(
      context,
    ).showSnackBar(SnackBar(content: Text(message)));
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
                  decoration: const InputDecoration(labelText: 'Calories'),
                ),
                TextField(
                  controller: proteinCtrl,
                  keyboardType: TextInputType.number,
                  decoration: const InputDecoration(labelText: 'Protein'),
                ),
                TextField(
                  controller: carbsCtrl,
                  keyboardType: TextInputType.number,
                  decoration: const InputDecoration(labelText: 'Carbs'),
                ),
                TextField(
                  controller: fatsCtrl,
                  keyboardType: TextInputType.number,
                  decoration: const InputDecoration(labelText: 'Fats'),
                ),
              ],
            ),
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.of(ctx).pop(),
              child: const Text('Cancel'),
            ),
            ElevatedButton(
              onPressed: () async {
                setState(() => _saving = true);
                try {
                  final updated = current.copyWith(
                    caloriesGoal:
                        double.tryParse(caloriesCtrl.text) ??
                        current.caloriesGoal,
                    proteinGoal:
                        double.tryParse(proteinCtrl.text) ??
                        current.proteinGoal,
                    carbsGoal:
                        double.tryParse(carbsCtrl.text) ?? current.carbsGoal,
                    fatsGoal:
                        double.tryParse(fatsCtrl.text) ?? current.fatsGoal,
                  );
                  await apiService.updateGoals(updated);
                  developer.log('Goals updated: ${updated.toJson()}');
                  _showSnack('Goals saved');
                  _fetch();
                  widget.onGoalsUpdated
                      ?.call(); // Call the callback to refresh home screen
                  if (mounted) Navigator.of(ctx).pop();
                } catch (e) {
                  developer.log('Update goals error: $e');
                  _showSnack('Failed to save goals');
                } finally {
                  if (mounted) setState(() => _saving = false);
                }
              },
              child: _saving
                  ? const SizedBox(
                      height: 16,
                      width: 16,
                      child: CircularProgressIndicator(strokeWidth: 2),
                    )
                  : const Text('Save'),
            ),
          ],
        );
      },
    );
  }

  Widget _metric(String label, String value, ThemeData theme) {
    return Column(
      children: [
        Text(
          value,
          style: theme.textTheme.titleLarge?.copyWith(
            fontWeight: FontWeight.bold,
          ),
        ),
        const SizedBox(height: 4),
        Text(label, style: theme.textTheme.bodyMedium),
      ],
    );
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Scaffold(
      appBar: AppBar(title: const Text('Goals')),
      body: FutureBuilder<List<Map<String, dynamic>>>(
        future: _goalsFuture,
        builder: (context, snapshot) {
          if (snapshot.connectionState == ConnectionState.waiting) {
            return const Center(child: CircularProgressIndicator());
          } else if (snapshot.hasError) {
            WidgetsBinding.instance.addPostFrameCallback(
              (_) => _showSnack('Error loading goals'),
            );
            return const Center(child: Text('Error'));
          } else if (snapshot.hasData && snapshot.data!.isNotEmpty) {
            final goals = snapshot.data!.map((g) => Goal.fromJson(g)).toList();
            final goal = goals.first;
            return SingleChildScrollView(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Card(
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(12),
                    ),
                    color: theme.colorScheme.primaryContainer,
                    child: Padding(
                      padding: const EdgeInsets.all(16),
                      child: Row(
                        mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                        children: [
                          _metric(
                            'Calories',
                            goal.caloriesGoal.toString(),
                            theme,
                          ),
                          _metric(
                            'Protein',
                            goal.proteinGoal.toString(),
                            theme,
                          ),
                          _metric('Carbs', goal.carbsGoal.toString(), theme),
                          _metric('Fats', goal.fatsGoal.toString(), theme),
                        ],
                      ),
                    ),
                  ),
                  const SizedBox(height: 16),
                  ElevatedButton(
                    onPressed: () => _editGoals(goal),
                    child: const Text('Edit Goals'),
                  ),
                ],
              ),
            );
          } else {
            return const Center(child: Text('No goals set'));
          }
        },
      ),
    );
  }
}
