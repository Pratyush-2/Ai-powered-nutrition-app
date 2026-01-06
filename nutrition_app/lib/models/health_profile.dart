class HealthProfile {
  final int? id;
  final int? userId;
  
  // Health Conditions
  final bool hasDiabetes;
  final String? diabetesType;
  final bool hasHighCholesterol;
  final bool hasHypertension;
  final bool hasHeartDisease;
  final bool hasKidneyDisease;
  final bool hasCeliac;
  
  // Food Intolerances
  final bool lactoseIntolerant;
  final bool glutenIntolerant;
  
  // Custom lists
  final List<String> allergies;
  final List<String> intolerances;
  final List<String> dietaryRestrictions;
  final List<String> avoidIngredients;
  
  final DateTime? createdAt;
  final DateTime? updatedAt;

  HealthProfile({
    this.id,
    this.userId,
    this.hasDiabetes = false,
    this.diabetesType,
    this.hasHighCholesterol = false,
    this.hasHypertension = false,
    this.hasHeartDisease = false,
    this.hasKidneyDisease = false,
    this.hasCeliac = false,
    this.lactoseIntolerant = false,
    this.glutenIntolerant = false,
    this.allergies = const [],
    this.intolerances = const [],
    this.dietaryRestrictions = const [],
    this.avoidIngredients = const [],
    this.createdAt,
    this.updatedAt,
  });

  factory HealthProfile.fromJson(Map<String, dynamic> json) {
    return HealthProfile(
      id: json['id'] as int?,
      userId: json['user_id'] as int?,
      hasDiabetes: json['has_diabetes'] as bool? ?? false,
      diabetesType: json['diabetes_type'] as String?,
      hasHighCholesterol: json['has_high_cholesterol'] as bool? ?? false,
      hasHypertension: json['has_hypertension'] as bool? ?? false,
      hasHeartDisease: json['has_heart_disease'] as bool? ?? false,
      hasKidneyDisease: json['has_kidney_disease'] as bool? ?? false,
      hasCeliac: json['has_celiac'] as bool? ?? false,
      lactoseIntolerant: json['lactose_intolerant'] as bool? ?? false,
      glutenIntolerant: json['gluten_intolerant'] as bool? ?? false,
      allergies: (json['allergies'] as List<dynamic>?)?.map((e) => e.toString()).toList() ?? [],
      intolerances: (json['intolerances'] as List<dynamic>?)?.map((e) => e.toString()).toList() ?? [],
      dietaryRestrictions: (json['dietary_restrictions'] as List<dynamic>?)?.map((e) => e.toString()).toList() ?? [],
      avoidIngredients: (json['avoid_ingredients'] as List<dynamic>?)?.map((e) => e.toString()).toList() ?? [],
      createdAt: json['created_at'] != null ? DateTime.parse(json['created_at']) : null,
      updatedAt: json['updated_at'] != null ? DateTime.parse(json['updated_at']) : null,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      if (id != null) 'id': id,
      if (userId != null) 'user_id': userId,
      'has_diabetes': hasDiabetes,
      'diabetes_type': diabetesType,
      'has_high_cholesterol': hasHighCholesterol,
      'has_hypertension': hasHypertension,
      'has_heart_disease': hasHeartDisease,
      'has_kidney_disease': hasKidneyDisease,
      'has_celiac': hasCeliac,
      'lactose_intolerant': lactoseIntolerant,
      'gluten_intolerant': glutenIntolerant,
      'allergies': allergies,
      'intolerances': intolerances,
      'dietary_restrictions': dietaryRestrictions,
      'avoid_ingredients': avoidIngredients,
    };
  }

  HealthProfile copyWith({
    int? id,
    int? userId,
    bool? hasDiabetes,
    String? diabetesType,
    bool? hasHighCholesterol,
    bool? hasHypertension,
    bool? hasHeartDisease,
    bool? hasKidneyDisease,
    bool? hasCeliac,
    bool? lactoseIntolerant,
    bool? glutenIntolerant,
    List<String>? allergies,
    List<String>? intolerances,
    List<String>? dietaryRestrictions,
    List<String>? avoidIngredients,
  }) {
    return HealthProfile(
      id: id ?? this.id,
      userId: userId ?? this.userId,
      hasDiabetes: hasDiabetes ?? this.hasDiabetes,
      diabetesType: diabetesType ?? this.diabetesType,
      hasHighCholesterol: hasHighCholesterol ?? this.hasHighCholesterol,
      hasHypertension: hasHypertension ?? this.hasHypertension,
      hasHeartDisease: hasHeartDisease ?? this.hasHeartDisease,
      hasKidneyDisease: hasKidneyDisease ?? this.hasKidneyDisease,
      hasCeliac: hasCeliac ?? this.hasCeliac,
      lactoseIntolerant: lactoseIntolerant ?? this.lactoseIntolerant,
      glutenIntolerant: glutenIntolerant ?? this.glutenIntolerant,
      allergies: allergies ?? this.allergies,
      intolerances: intolerances ?? this.intolerances,
      dietaryRestrictions: dietaryRestrictions ?? this.dietaryRestrictions,
      avoidIngredients: avoidIngredients ?? this.avoidIngredients,
      createdAt: createdAt,
      updatedAt: DateTime.now(),
    );
  }
}

class HealthWarning {
  final String type;
  final String severity;
  final String message;
  final String icon;

  HealthWarning({
    required this.type,
    required this.severity,
    required this.message,
    required this.icon,
  });

  factory HealthWarning.fromJson(Map<String, dynamic> json) {
    return HealthWarning(
      type: json['type'] as String,
      severity: json['severity'] as String,
      message: json['message'] as String,
      icon: json['icon'] as String,
    );
  }

  bool get isCritical => severity == 'critical';
  bool get isWarning => severity == 'warning';
  bool get isInfo => severity == 'info';
}
