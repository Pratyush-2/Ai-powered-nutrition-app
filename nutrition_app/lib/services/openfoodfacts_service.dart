import 'dart:convert';
import 'package:http/http.dart' as http;
import 'dart:developer' as developer;

class OpenFoodFactsService {
  final String _baseUrl = 'https://world.openfoodfacts.org/api/v2/product/';

  Future<Map<String, dynamic>> searchFood(String query) async {
    final uri = Uri.parse('$_baseUrl?search_terms=$query&fields=product_name,nutriments,code');
    developer.log('Searching Open Food Facts: $uri');
    final response = await http.get(uri);

    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    } else {
      developer.log('Open Food Facts API Error: ${response.statusCode} ${response.body}');
      throw Exception('Failed to search food: ${response.statusCode} ${response.body}');
    }
  }

  Future<Map<String, dynamic>> getProductByBarcode(String barcode) async {
    final uri = Uri.parse('$_baseUrl$barcode?fields=product_name,nutriments,code');
    developer.log('Fetching product by barcode: $uri');
    final response = await http.get(uri);

    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    } else {
      developer.log('Open Food Facts API Error: ${response.statusCode} ${response.body}');
      throw Exception('Failed to fetch product by barcode: ${response.statusCode} ${response.body}');
    }
  }
}
