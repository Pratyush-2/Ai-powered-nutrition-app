class UserProfileModel {
  final int id;
  final String name;
  final double age;
  final double heightCm;
  final double weightKg;
  final String gender;
  final String activityLevel;
  final String? goal;

  UserProfileModel({
    required this.id,
    required this.name,
    required this.age,
    required this.heightCm,
    required this.weightKg,
    required this.gender,
    required this.activityLevel,
    this.goal,
  });

  factory UserProfileModel.fromJson(Map<String, dynamic> json) {
    return UserProfileModel(
      id: json['id'] as int,
      name: json['name'] as String,
      age: (json['age'] as num).toDouble(),
      heightCm: (json['height_cm'] as num).toDouble(),
      weightKg: (json['weight_kg'] as num).toDouble(),
      gender: json['gender'] as String,
      activityLevel: json['activity_level'] as String,
      goal: json['goal'] as String?,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      'age': age,
      'height_cm': heightCm,
      'weight_kg': weightKg,
      'gender': gender,
      'activity_level': activityLevel,
      'goal': goal,
    };
  }
}


