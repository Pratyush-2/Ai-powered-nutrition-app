class Food {
  final int? id;
  final String name;
  final String? barcode;
  final double calories;
  final double protein;
  final double carbs;
  final double fats;
  final String? servingSize;
  final bool isLocalData; // Add this field

  Food({
    this.id,
    required this.name,
    this.barcode,
    required this.calories,
    required this.protein,
    required this.carbs,
    required this.fats,
    this.servingSize,
    this.isLocalData = false, // Default to false
  });

  factory Food.fromJson(Map<String, dynamic> json) {
    return Food(
      id: json['id'] as int?,
      name: json['name'] as String,
      barcode: json['barcode'] as String?,
      calories: (json['calories'] as num).toDouble(),
      protein: (json['protein'] as num).toDouble(),
      carbs: (json['carbs'] as num).toDouble(),
      fats: (json['fats'] as num).toDouble(),
      servingSize: json['serving_size'] as String?,
      isLocalData: false, // Not applicable for JSON
    );
  }

  factory Food.fromOpenFoodFacts(Map<String, dynamic> json) {
    final nutriments = json['nutriments'] as Map<String, dynamic>? ?? {};
    
    // Debug: Print the keys to see what's available
    print('🔍 OpenFoodFacts JSON keys: ${json.keys.toList()}');
    
    // Helper function to safely convert string/num to double
    double safeConvertToDouble(dynamic value) {
      if (value == null) return 0.0;
      if (value is num) return value.toDouble();
      if (value is String) {
        return double.tryParse(value) ?? 0.0;
      }
      return 0.0;
    }
    
    // Extract product name from various possible fields (expanded list)
    String productName = 'Unknown Food';
    
    // Check all possible name fields in order of preference
    final possibleNameFields = [
      'product_name',
      'product_name_en', 
      'product_name_fr',
      'product_name_de',
      'product_name_es',
      'product_name_it',
      'generic_name',
      'generic_name_en',
      'generic_name_fr',
      'name',  // Some APIs might use this
      'product', // Fallback
      'brands', // Sometimes just the brand
    ];
    
    for (final field in possibleNameFields) {
      if (json[field] != null) {
        final value = json[field].toString().trim();
        if (value.isNotEmpty) {
          productName = value;
          print('✅ Found product name in field "$field": $productName');
          break;
        }
      }
    }
    
    // If still unknown, try to construct from other fields
    if (productName == 'Unknown Food') {
      final brand = json['brands']?.toString().trim() ?? '';
      final category = json['categories']?.toString().trim() ?? '';
      if (brand.isNotEmpty && category.isNotEmpty) {
        productName = '$brand $category';
      } else if (brand.isNotEmpty) {
        productName = brand;
      } else if (category.isNotEmpty) {
        productName = category;
      }
      print('⚠️ Constructed product name: $productName');
    }
    
    print('🏷️ Final product name: $productName');
    
    return Food(
      id: null, // Will be assigned by the backend
      name: productName,
      barcode: json['code'] as String?,
      calories: safeConvertToDouble(nutriments['energy-kcal_100g'] ?? nutriments['energy-kcal']),
      protein: safeConvertToDouble(nutriments['proteins_100g'] ?? nutriments['proteins']),
      carbs: safeConvertToDouble(nutriments['carbohydrates_100g'] ?? nutriments['carbohydrates']),
      fats: safeConvertToDouble(nutriments['fat_100g'] ?? nutriments['fat']),
      servingSize: json['serving_size'] as String? ?? '100g',
      // Add source indicator
      isLocalData: json['_local_fallback'] == true,
    );
  }

  Map<String, dynamic> toJson() {
    final Map<String, dynamic> data = {
      'name': name,
      'calories': calories,
      'protein': protein,
      'carbs': carbs,
      'fats': fats,
    };
    if (barcode != null) {
      data['barcode'] = barcode;
    }
    if (servingSize != null) {
      data['serving_size'] = servingSize;
    }
    return data;
  }
}


