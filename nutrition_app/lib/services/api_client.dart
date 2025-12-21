import 'package:nutrition_app/services/api_service.dart';

class ApiConfig {
  static String get baseUrl {
    // Force Android emulator base URL per requirements
    return 'http://10.0.2.2:8000';
  }
}

final String apiUrl = ApiConfig.baseUrl;
final ApiService apiService = ApiService(apiUrl);
