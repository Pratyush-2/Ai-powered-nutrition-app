import 'dart:convert';
import 'dart:io'; // Add this import for File
import 'package:http/http.dart' as http;
// import 'dart:developer' as developer;
import '../models/goal.dart';
import '../models/food.dart';
import '../models/log.dart';
// import '../models/profile.dart';
import 'package:http_parser/http_parser.dart'
    as http_parser; // Added this import for MediaType

class ApiService {
  final String baseUrl;

  ApiService(this.baseUrl);

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

  Future<Map<String, dynamic>> identifyFood(String imagePath) async {
    final uri = Uri.parse('$baseUrl/ai/identify-food/');
    final request = http.MultipartRequest('POST', uri);
    request.files.add(await http.MultipartFile.fromPath('file', imagePath));
    final response = await request.send();
    final responseBody = await response.stream.bytesToString();

    print('🔍 Raw Response: $responseBody'); // Add this debug

    if (response.statusCode >= 200 && response.statusCode < 300) {
      final parsed = jsonDecode(responseBody); // This might fail
      print('🔍 Parsed Response Type: ${parsed.runtimeType}'); // Add this
      return parsed;
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
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode(food.toJson()),
    );
    final data = _handleResponse(response);
    return Food.fromJson(data);
  }

  Future<void> deleteLog(String logId) async {
    final url = Uri.parse('$baseUrl/logs/$logId');
    final response = await http.delete(url);
    if (response.statusCode < 200 || response.statusCode >= 300) {
      throw Exception(
        'Failed to delete log (status: ${response.statusCode}): ${response.body}',
      );
    }
  }

  Future<List<Food>> searchFood(String foodName) async {
    final uri = Uri.parse('$baseUrl/search-food/$foodName');
    final response = await http.get(uri);
    final data = _handleResponse(response) as Map<String, dynamic>;
    final products = data['products'] as List<dynamic>;
    
    // Debug: Print first product structure
    if (products.isNotEmpty) {
      print('🔍 First product keys: ${products.first.keys}');
      print('🔍 First product sample: ${products.first}');
    }
    
    return products
        .map((p) => Food.fromOpenFoodFacts(p as Map<String, dynamic>))
        .toList();
  }

  Future<Map<String, dynamic>> getTotals(int userId, String date) async {
    final uri = Uri.parse('$baseUrl/totals/$userId/$date');
    final response = await http.get(uri);
    return _handleResponse(response);
  }

  Future<List<DailyLogModel>> getLogs(int userId, String logDate) async {
    final uri = Uri.parse(
      '$baseUrl/logs/?user_id=$userId&log_date=$logDate',
    ); // Changed 'date' to 'log_date'
    final response = await http.get(uri);
    final data = _handleResponse(response) as List<dynamic>;
    return data
        .map((e) => DailyLogModel.fromJson(e as Map<String, dynamic>))
        .toList();
  }

  Future<Map<String, dynamic>> addLog(Map<String, dynamic> logData) async {
    final uri = Uri.parse('$baseUrl/logs/');
    final response = await http.post(
      uri,
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode(logData),
    );
    return _handleResponse(response);
  }

  Future<List<Map<String, dynamic>>> getAllGoals() async {
    final uri = Uri.parse('$baseUrl/goals/all/');
    final response = await http.get(uri);
    final data = _handleResponse(response) as List<dynamic>;
    return data.cast<Map<String, dynamic>>().toList();
  }

  Future<Map<String, dynamic>> createProfile(
    Map<String, dynamic> profileData,
  ) async {
    final uri = Uri.parse('$baseUrl/profiles/');
    final response = await http.post(
      uri,
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode(profileData),
    );
    return _handleResponse(response);
  }

  Future<Map<String, dynamic>> getProfileById(int profileId) async {
    final uri = Uri.parse('$baseUrl/profiles/$profileId');
    final response = await http.get(uri);
    return _handleResponse(response);
  }

  Future<Map<String, dynamic>> classifyFood(int userId, String foodName) async {
    final uri = Uri.parse('$baseUrl/ai/classify/');
    final response = await http.post(
      uri,
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'user_id': userId, 'food_name': foodName}),
    );
    return _handleResponse(response);
  }

  Future<Map<String, dynamic>> chat(int userId, String query) async {
    final uri = Uri.parse('$baseUrl/ai/chat/');
    final response = await http.post(
      uri,
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'user_id': userId, 'query': query}),
    );
    return _handleResponse(response);
  }

  // Additional methods needed by other screens
  Future<List<Goal>> getGoals(int userId) async {
    final uri = Uri.parse('$baseUrl/goals/$userId');
    final response = await http.get(uri);
    final data = _handleResponse(response) as List<dynamic>;
    return data.map((g) => Goal.fromJson(g as Map<String, dynamic>)).toList();
  }

  Future<Map<String, dynamic>> updateGoals(Goal goal) async {
    final uri = Uri.parse('$baseUrl/goals/${goal.id}');
    final response = await http.put(
      uri,
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode(goal.toJson()),
    );
    return _handleResponse(response);
  }

  Future<Map<String, dynamic>> updateProfile(
    Map<String, dynamic> profileData,
  ) async {
    final uri = Uri.parse('$baseUrl/profiles/${profileData['id']}');
    final response = await http.put(
      uri,
      headers: {'Content-Type': 'application/json'},
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
      headers: {'Content-Type': 'application/json'},
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
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode(logData),
    );
    return _handleResponse(response);
  }

  Future<Map<String, dynamic>> scanBarcode(File imageFile) async {
    final uri = Uri.parse('$baseUrl/ai/scan-barcode/');
    final request = http.MultipartRequest('POST', uri);

    request.files.add(
      await http.MultipartFile.fromPath(
        'file',
        imageFile.path,
        contentType: http_parser.MediaType('image', 'jpeg'),
      ),
    );

    final response = await request.send();
    final responseData = await response.stream.toBytes();
    final responseString = String.fromCharCodes(responseData);

    if (response.statusCode == 200) {
      return json.decode(responseString);
    } else {
      throw Exception('Barcode scan failed');
    }
  }

  Future<Map<String, dynamic>> analyzeSugar(
    String foodName,
    double totalSugar,
    Map<String, dynamic>? nutritionalData,
  ) async {
    final response = await http.post(
      Uri.parse('$baseUrl/ai/analyze-sugar/'),
      headers: {'Content-Type': 'application/json'},
      body: json.encode({
        'food_name': foodName,
        'total_sugar': totalSugar,
        'nutritional_data': nutritionalData,
      }),
    );

    if (response.statusCode == 200) {
      return json.decode(response.body);
    } else {
      throw Exception('Sugar analysis failed');
    }
  }

  Future<Map<String, dynamic>> comprehensiveNutritionAnalysis(
    String foodName,
    int userId,
  ) async {
    final response = await http.post(
      Uri.parse('$baseUrl/ai/nutrition-analysis/'),
      headers: {'Content-Type': 'application/json'},
      body: json.encode({'food_name': foodName, 'user_id': userId}),
    );

    if (response.statusCode == 200) {
      return json.decode(response.body);
    } else {
      throw Exception('Nutrition analysis failed');
    }
  }
}
