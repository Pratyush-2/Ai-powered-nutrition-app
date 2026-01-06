import 'dart:convert';
import 'dart:io';
import 'package:http/http.dart' as http;
import 'package:http_parser/http_parser.dart' as http_parser;
import 'package:nutrition_app/services/auth_service.dart';
import '../models/goal.dart';
import '../models/food.dart';
import '../models/log.dart';

class ApiService {
  final String baseUrl;
  final AuthService _authService = AuthService();

  ApiService(this.baseUrl);

  Future<Map<String, String>> _getAuthHeaders() async {
    final token = await _authService.getToken();
    return {
      'Content-Type': 'application/json',
      'Authorization': 'Bearer $token',
    };
  }

  dynamic _handleResponse(http.Response response) {
    if (response.statusCode >= 200 && response.statusCode < 300) {
      if (response.body.isEmpty) return null;
      return jsonDecode(response.body);
    } else {
      throw Exception(
        'API Error (status ${response.statusCode}): ${response.body}',
      );
    }
  }

  Future<Map<String, dynamic>> login(String email, String password) async {
    final uri = Uri.parse('$baseUrl/auth/login');
    final response = await http.post(
      uri,
      headers: {'Content-Type': 'application/x-www-form-urlencoded'},
      body: {'username': email, 'password': password},
    );
    final data = _handleResponse(response);
    await _authService.saveToken(data['access_token']);
    return data;
  }

  Future<Map<String, dynamic>> register(Map<String, dynamic> profileData) async {
    final uri = Uri.parse('$baseUrl/auth/register');
    final response = await http.post(
      uri,
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode(profileData),
    );
    return _handleResponse(response);
  }

  Future<void> logout() async {
    await _authService.deleteToken();
  }

  Future<Map<String, dynamic>> identifyFood(String imagePath) async {
    final uri = Uri.parse('$baseUrl/ai/identify-food/');
    final request = http.MultipartRequest('POST', uri);
    request.headers.addAll(await _getAuthHeaders());
    request.files.add(await http.MultipartFile.fromPath('file', imagePath));
    final response = await request.send().timeout(const Duration(seconds: 30));
    final responseBody = await response.stream.bytesToString();

    if (response.statusCode >= 200 && response.statusCode < 300) {
      return jsonDecode(responseBody);
    } else {
      throw Exception(
        'Failed to identify food: ${response.statusCode} $responseBody',
      );
    }
  }

  Future<Food> createFood(Food food) async {
    final uri = Uri.parse('$baseUrl/foods/');
    final response = await http.post(
      uri,
      headers: await _getAuthHeaders(),
      body: jsonEncode(food.toJson()),
    );
    final data = _handleResponse(response);
    return Food.fromJson(data);
  }

  Future<void> deleteLog(String logId) async {
    final url = Uri.parse('$baseUrl/logs/$logId');
    final response = await http.delete(url, headers: await _getAuthHeaders());
    if (response.statusCode < 200 || response.statusCode >= 300) {
      throw Exception(
        'Failed to delete log (status: ${response.statusCode}): ${response.body}',
      );
    }
  }

  Future<List<Food>> searchFood(String foodName) async {
    final uri = Uri.parse('$baseUrl/search-food/$foodName');
    final response = await http.get(uri, headers: await _getAuthHeaders());
    final data = _handleResponse(response) as Map<String, dynamic>;
    final products = data['products'] as List<dynamic>;
    return products
        .map((p) => Food.fromOpenFoodFacts(p as Map<String, dynamic>))
        .toList();
  }

  Future<Map<String, dynamic>> getTotals(String date) async {
    final uri = Uri.parse('$baseUrl/totals/$date');
    final response = await http.get(uri, headers: await _getAuthHeaders());
    return _handleResponse(response);
  }

  Future<List<DailyLogModel>> getLogs(String logDate) async {
    final uri = Uri.parse('$baseUrl/logs/?log_date=$logDate');
    final response = await http.get(uri, headers: await _getAuthHeaders());
    final data = _handleResponse(response) as List<dynamic>;
    return data
        .map((e) => DailyLogModel.fromJson(e as Map<String, dynamic>))
        .toList();
  }

  Future<Map<String, dynamic>> addLog(Map<String, dynamic> logData) async {
    final uri = Uri.parse('$baseUrl/logs/');
    final response = await http.post(
      uri,
      headers: await _getAuthHeaders(),
      body: jsonEncode(logData),
    );
    return _handleResponse(response);
  }

  Future<Map<String, dynamic>> getProfile() async {
    final uri = Uri.parse('$baseUrl/profiles/me');
    final response = await http.get(uri, headers: await _getAuthHeaders());
    return _handleResponse(response);
  }

  Future<Map<String, dynamic>> classifyFood(String foodName) async {
    final uri = Uri.parse('$baseUrl/ai/classify/');
    final response = await http.post(
      uri,
      headers: await _getAuthHeaders(),
      body: jsonEncode({'food_name': foodName}),
    ).timeout(const Duration(seconds: 30));
    return _handleResponse(response);
  }

  Future<Map<String, dynamic>> chat(String query) async {
    final uri = Uri.parse('$baseUrl/ai/chat/');
    final response = await http.post(
      uri,
      headers: await _getAuthHeaders(),
      body: jsonEncode({'query': query}),
    ).timeout(const Duration(seconds: 30));
    return _handleResponse(response);
  }

  Future<List<Goal>> getGoals() async {
    final uri = Uri.parse('$baseUrl/goals/');
    final response = await http.get(uri, headers: await _getAuthHeaders());
    final data = _handleResponse(response) as List<dynamic>;
    return data.map((g) => Goal.fromJson(g as Map<String, dynamic>)).toList();
  }

  Future<Map<String, dynamic>> updateGoals(Goal goal) async {
    final uri = Uri.parse('$baseUrl/goals/${goal.id}');
    final response = await http.put(
      uri,
      headers: await _getAuthHeaders(),
      body: jsonEncode(goal.toJson()),
    );
    return _handleResponse(response);
  }

  Future<Map<String, dynamic>> updateProfile(
    Map<String, dynamic> profileData,
  ) async {
    final uri = Uri.parse('$baseUrl/profiles/');
    final response = await http.put(
      uri,
      headers: await _getAuthHeaders(),
      body: jsonEncode(profileData),
    );
    return _handleResponse(response);
  }

  Future<Map<String, dynamic>> setUserGoal(
    Map<String, dynamic> goalData,
  ) async {
    final uri = Uri.parse('$baseUrl/goals/');
    final response = await http.post(
      uri,
      headers: await _getAuthHeaders(),
      body: jsonEncode(goalData),
    );
    return _handleResponse(response);
  }


  Future<Map<String, dynamic>> updateLog(
    int logId,
    Map<String, dynamic> logData,
  ) async {
    final uri = Uri.parse('$baseUrl/logs/$logId');
    final response = await http.put(
      uri,
      headers: await _getAuthHeaders(),
      body: jsonEncode(logData),
    );
    return _handleResponse(response);
  }

  // Health Profile
  Future<Map<String, dynamic>> getHealthProfile() async {
    final uri = Uri.parse('$baseUrl/health-profile/');
    final response = await http.get(uri, headers: await _getAuthHeaders());
    return _handleResponse(response);
  }

  Future<Map<String, dynamic>> createHealthProfile(
    Map<String, dynamic> profileData,
  ) async {
    final uri = Uri.parse('$baseUrl/health-profile/');
    final response = await http.post(
      uri,
      headers: await _getAuthHeaders(),
      body: jsonEncode(profileData),
    );
    return _handleResponse(response);
  }

  Future<Map<String, dynamic>> updateHealthProfile(
    Map<String, dynamic> profileData,
  ) async {
    final uri = Uri.parse('$baseUrl/health-profile/');
    final response = await http.put(
      uri,
      headers: await _getAuthHeaders(),
      body: jsonEncode(profileData),
    );
    return _handleResponse(response);
  }

  Future<List<Map<String, dynamic>>> checkFoodSafety(
    int foodId,
    double quantity,
  ) async {
    final uri = Uri.parse('$baseUrl/check-food-safety/');
    final response = await http.post(
      uri,
      headers: await _getAuthHeaders(),
      body: jsonEncode({
        'food_id': foodId,
        'quantity': quantity,
      }),
    );
    final data = _handleResponse(response);
    return (data as List<dynamic>).map((e) => e as Map<String, dynamic>).toList();
  }
}
