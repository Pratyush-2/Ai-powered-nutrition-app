import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import 'dart:developer' as developer;
import 'package:nutrition_app/models/goal.dart';
import 'package:nutrition_app/models/log.dart';
import 'package:nutrition_app/main.dart';
import 'package:nutrition_app/widgets/calorie_progress_card.dart';
import 'package:nutrition_app/widgets/macro_progress.dart';
import 'package:nutrition_app/widgets/meal_card_with_recommendation.dart';
import 'package:nutrition_app/screens/log_food_screen.dart';
import 'package:nutrition_app/screens/chat_screen.dart';

class HomeScreen extends StatefulWidget {
  final bool isGuest;
  const HomeScreen({super.key, this.isGuest = false});

  @override
  State<HomeScreen> createState() => HomeScreenState();
}

class HomeScreenState extends State<HomeScreen> {
  late Future<Map<String, dynamic>> _homeDataFuture;

  @override
  void initState() {
    super.initState();
    _homeDataFuture = _getHomeData();
  }

  void refreshData() {
    if (mounted) {
      setState(() {
        _homeDataFuture = _getHomeData();
      });
    }
  }

  Future<Map<String, dynamic>> _getHomeData() async {
    final today = DateFormat('yyyy-MM-dd').format(DateTime.now());
    try {
      final results = await Future.wait([
        apiService.getTotals(today),
        apiService.getGoals(),
        apiService.getLogs(today),
        apiService.getProfile(),
      ]);
      return {
        'totals': results[0],
        'goals': results[1],
        'logs': results[2],
        'profile': results[3],
      };
    } catch (e) {
      developer.log('Error fetching home screen data: $e', name: 'HomeScreen');
      rethrow;
    }
  }

  Future<void> _deleteLog(int logId) async {
    final bool? confirmed = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Delete Log'),
        content: const Text('Are you sure you want to delete this food log?'),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(false),
            child: const Text('Cancel'),
          ),
          TextButton(
            onPressed: () => Navigator.of(context).pop(true),
            child: const Text('Delete'),
          ),
        ],
      ),
    );

    if (confirmed == true) {
      try {
        await apiService.deleteLog(logId.toString());
        if (mounted) {
          ScaffoldMessenger.of(context)
            ..removeCurrentSnackBar()
            ..showSnackBar(
              const SnackBar(content: Text('Log deleted successfully')),
            );
        }
        refreshData();
      } catch (e) {
        if (mounted) {
          ScaffoldMessenger.of(context)
            ..removeCurrentSnackBar()
            ..showSnackBar(SnackBar(content: Text('Failed to delete log: $e')));
        }
      }
    }
  }

  Future<void> _editLog(int logId) async {
    final logs = await _getHomeData().then(
      (data) => data['logs'] as List<DailyLogModel>,
    );
    final logToEdit = logs.firstWhere((log) => log.id == logId);

    if (!mounted) return;

    final result = await Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => LogFoodScreen(
          editLog: logToEdit,
        ),
      ),
    );

    if (result == true && mounted) {
      refreshData();
    }
  }

  void _chatAboutFood(DailyLogModel log) {
    if (log.food == null) return;
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => ChatScreen(
          initialPrompt: 'Is ${log.food!.name} a good choice for me? Give me a small explanation.',
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Scaffold(
      body: FutureBuilder<Map<String, dynamic>>(
        future: _homeDataFuture,
        builder: (context, snapshot) {
          if (snapshot.connectionState == ConnectionState.waiting) {
            return const Center(child: CircularProgressIndicator());
          }
          if (snapshot.hasError) {
            return Center(child: Text('Error: ${snapshot.error}'));
          }
          if (snapshot.hasData) {
            final homeData = snapshot.data!;
            final totals = homeData['totals'] as Map<String, dynamic>;
            final goals = homeData['goals'] as List<Goal>;
            final logs = homeData['logs'] as List<DailyLogModel>;
            final profile = homeData['profile'] as Map<String, dynamic>;
            final goal = goals.isNotEmpty ? goals.first : null;
            final caloriesConsumed =
                (totals['calories'] as num?)?.toDouble() ?? 0.0;
            final caloriesGoal = goal?.caloriesGoal ?? 2000.0;

            return CustomScrollView(
              slivers: [
                SliverAppBar(
                  expandedHeight: 120.0,
                  pinned: true,
                  flexibleSpace: FlexibleSpaceBar(
                    title: Text(
                      'Good morning, ${profile['name'] ?? 'User'}!',
                      style: theme.textTheme.titleLarge,
                    ),
                  ),
                ),
                SliverPadding(
                  padding: const EdgeInsets.all(16.0),
                  sliver: SliverToBoxAdapter(
                    child: CalorieProgressCard(
                      caloriesConsumed: caloriesConsumed,
                      caloriesGoal: caloriesGoal,
                    ),
                  ),
                ),
                SliverPadding(
                  padding: const EdgeInsets.symmetric(
                    horizontal: 16.0,
                    vertical: 8.0,
                  ),
                  sliver: SliverToBoxAdapter(
                    child: goal != null
                        ? Column(
                            children: [
                              MacroProgress(
                                label: 'Protein',
                                current:
                                    (totals['protein'] as num?)?.toDouble() ??
                                    0.0,
                                goal: goal.proteinGoal,
                              ),
                              const SizedBox(height: 16),
                              MacroProgress(
                                label: 'Carbs',
                                current:
                                    (totals['carbs'] as num?)?.toDouble() ??
                                    0.0,
                                goal: goal.carbsGoal,
                              ),
                              const SizedBox(height: 16),
                              MacroProgress(
                                label: 'Fats',
                                current:
                                    (totals['fats'] as num?)?.toDouble() ?? 0.0,
                                goal: goal.fatsGoal,
                              ),
                            ],
                          )
                        : const Text('Set a goal to see macro progress.'),
                  ),
                ),
                SliverToBoxAdapter(
                  child: Padding(
                    padding: const EdgeInsets.all(16),
                    child: Text(
                      'Recent meals',
                      style: theme.textTheme.headlineSmall,
                    ),
                  ),
                ),
                if (logs.isNotEmpty)
                  SliverList(
                    delegate: SliverChildBuilderDelegate((context, index) {
                      final log = logs[index];
                      return MealCardWithRecommendation(
                        log: log,
                        onEdit: () => _editLog(log.id),
                        onDelete: () => _deleteLog(log.id),
                        onChat: () => _chatAboutFood(log),
                      );
                    }, childCount: logs.length),
                  )
                else
                  SliverToBoxAdapter(
                    child: Center(
                      child: Padding(
                        padding: const EdgeInsets.symmetric(vertical: 32.0),
                        child: Text(
                          'No meals logged today.',
                          style: theme.textTheme.bodyMedium,
                        ),
                      ),
                    ),
                  ),
              ],
            );
          }
          return const Center(child: Text('No data available.'));
        },
      ),
    );
  }
}
