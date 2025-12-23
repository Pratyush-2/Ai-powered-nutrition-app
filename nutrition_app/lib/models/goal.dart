class Goal {
  final int id;
  final int userId;
  final double caloriesGoal;
  final double proteinGoal;
  final double carbsGoal;
  final double fatsGoal;

  Goal({
    required this.id,
    required this.userId,
    required this.caloriesGoal,
    required this.proteinGoal,
    required this.carbsGoal,
    required this.fatsGoal,
  });

  factory Goal.fromJson(Map<String, dynamic> json) {
    return Goal(
      id: json['id'] as int,
      userId: json['user_id'] as int,
      caloriesGoal: (json['calories_goal'] as num).toDouble(),
      proteinGoal: (json['protein_goal'] as num).toDouble(),
      carbsGoal: (json['carbs_goal'] as num).toDouble(),
      fatsGoal: (json['fats_goal'] as num).toDouble(),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'user_id': userId,
      'calories_goal': caloriesGoal,
      'protein_goal': proteinGoal,
      'carbs_goal': carbsGoal,
      'fats_goal': fatsGoal,
    };
  }

  Goal copyWith({
    int? id,
    int? userId,
    double? caloriesGoal,
    double? proteinGoal,
    double? carbsGoal,
    double? fatsGoal,
  }) {
    return Goal(
      id: id ?? this.id,
      userId: userId ?? this.userId,
      caloriesGoal: caloriesGoal ?? this.caloriesGoal,
      proteinGoal: proteinGoal ?? this.proteinGoal,
      carbsGoal: carbsGoal ?? this.carbsGoal,
      fatsGoal: fatsGoal ?? this.fatsGoal,
    );
  }
}


