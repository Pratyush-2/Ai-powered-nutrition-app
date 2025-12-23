import 'package:shared_preferences/shared_preferences.dart';
import 'dart:convert';
import '../models/log.dart';
import '../models/goal.dart';

/// Local storage service for guest users
/// Stores all data locally using SharedPreferences
class GuestDataService {
  static const String _logsKey = 'guest_logs';
  static const String _goalsKey = 'guest_goals';

  // Save logs for a specific date
  Future<void> saveLogs(String date, List<DailyLogModel> logs) async {
    final prefs = await SharedPreferences.getInstance();
    final allLogs = await _getAllLogs();
    allLogs[date] = logs.map((log) => log.toJson()).toList();
    await prefs.setString(_logsKey, jsonEncode(allLogs));
  }

  // Get logs for a specific date
  Future<List<DailyLogModel>> getLogs(String date) async {
    final allLogs = await _getAllLogs();
    final logsJson = allLogs[date] as List<dynamic>?;
    if (logsJson == null) return [];
    return logsJson.map((json) => DailyLogModel.fromJson(json)).toList();
  }

  // Add a log entry
  Future<void> addLog(DailyLogModel log) async {
    final dateStr = log.date.toIso8601String().split('T')[0];
    final logs = await getLogs(dateStr);
    logs.add(log);
    await saveLogs(dateStr, logs);
  }

  // Delete a log entry
  Future<void> deleteLog(String date, int logId) async {
    final logs = await getLogs(date);
    logs.removeWhere((log) => log.id == logId);
    await saveLogs(date, logs);
  }

  // Get all logs (internal helper)
  Future<Map<String, dynamic>> _getAllLogs() async {
    final prefs = await SharedPreferences.getInstance();
    final logsString = prefs.getString(_logsKey);
    if (logsString == null) return {};
    return jsonDecode(logsString) as Map<String, dynamic>;
  }

  // Get totals for a specific date
  Future<Map<String, double>> getTotals(String date) async {
    final logs = await getLogs(date);
    double calories = 0;
    double protein = 0;
    double carbs = 0;
    double fats = 0;

    for (final log in logs) {
      if (log.food != null) {
        final multiplier = log.quantity / 100;
        calories += log.food!.calories * multiplier;
        protein += log.food!.protein * multiplier;
        carbs += log.food!.carbs * multiplier;
        fats += log.food!.fats * multiplier;
      }
    }

    return {
      'calories': calories,
      'protein': protein,
      'carbs': carbs,
      'fats': fats,
    };
  }

  // Save goals
  Future<void> saveGoals(Goal goal) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_goalsKey, jsonEncode(goal.toJson()));
  }

  // Get goals
  Future<Goal?> getGoals() async {
    final prefs = await SharedPreferences.getInstance();
    final goalsString = prefs.getString(_goalsKey);
    if (goalsString == null) return null;
    return Goal.fromJson(jsonDecode(goalsString));
  }

  // Clear all guest data
  Future<void> clearAllData() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove(_logsKey);
    await prefs.remove(_goalsKey);
  }
}
