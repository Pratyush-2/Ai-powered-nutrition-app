import 'package:nutrition_app/services/api_service.dart';

class ApiConfig {
  static String get baseUrl {
    // Production API hosted on Render
    return 'https://ai-powered-nutrition-app.onrender.com';
  }
}

final String apiUrl = ApiConfig.baseUrl;
final ApiService apiService = ApiService(apiUrl);
