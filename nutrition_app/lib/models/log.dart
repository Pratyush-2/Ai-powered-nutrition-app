import 'food.dart';

class DailyLogModel {
  final int id;
  final int foodId;
  final double quantity;
  final DateTime date;
  final Food? food;

  DailyLogModel({
    required this.id,
    required this.foodId,
    required this.quantity,
    required this.date,
    this.food,
  });

  factory DailyLogModel.fromJson(Map<String, dynamic> json) {
    return DailyLogModel(
      id: json['id'] as int,
      foodId: json['food_id'] as int,
      quantity: (json['quantity'] as num).toDouble(),
      date: DateTime.parse(json['date'].toString()),
      food: json['food'] != null ? Food.fromJson(json['food'] as Map<String, dynamic>) : null,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'food_id': foodId,
      'quantity': quantity,
      'date': date.toIso8601String(),
      'food': food?.toJson(),
    };
  }
}


