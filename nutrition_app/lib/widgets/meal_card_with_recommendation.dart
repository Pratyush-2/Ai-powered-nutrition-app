import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import 'package:nutrition_app/models/log.dart';
import 'package:nutrition_app/services/api_client.dart';
import 'meal_card.dart';

class MealCardWithRecommendation extends StatefulWidget {
  final DailyLogModel log;
  final int userId;
  final VoidCallback? onEdit;
  final VoidCallback? onDelete;

  const MealCardWithRecommendation({
    super.key,
    required this.log,
    required this.userId,
    this.onEdit,
    this.onDelete,
  });

  @override
  State<MealCardWithRecommendation> createState() => _MealCardWithRecommendationState();
}

class _MealCardWithRecommendationState extends State<MealCardWithRecommendation> {
  String _recommendation = 'Loading...';

  @override
  void initState() {
    super.initState();
    _fetchRecommendation();
  }

  Future<void> _fetchRecommendation() async {
    if (widget.log.food == null) {
      if (mounted) {
        setState(() {
          _recommendation = 'N/A';
        });
      }
      return;
    }

    try {
      print('🔍 Starting food classification for: ${widget.log.food!.name}');
      final result = await apiService.classifyFood(widget.userId, widget.log.food!.name);
      
      print('🔍 API Response: $result');
      
      // Handle the current API response format
      if (result.containsKey('recommendation')) {
        final isRecommended = result['recommendation'] == 'recommended';
        final confidence = result['confidence'] ?? 0.0;
        final score = result['health_score'] ?? 0.0;
        
        print('✅ Recommendation result: recommended=$isRecommended, score=$score, confidence=$confidence');
        
        String recommendationText;
        if (isRecommended) {
          recommendationText = 'Recommended (${(confidence * 100).toInt()}% confidence)';
        } else {
          recommendationText = 'Not recommended (${(confidence * 100).toInt()}% confidence)';
        }
        
        if (mounted) {
          setState(() {
            _recommendation = recommendationText;
          });
        }
      } else {
        print('❌ Missing "recommendation" field in response');
        if (mounted) {
          setState(() {
            _recommendation = 'Invalid API response';
          });
        }
      }
    } catch (e) {
      print('❌ Recommendation error: $e');
      if (mounted) {
        setState(() {
          _recommendation = 'Recommendation error: $e';
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final food = widget.log.food;
    if (food == null) return const SizedBox.shrink();

    return MealCard(
      title: food.name,
      kcal: food.calories.toInt(),
      time: DateFormat('yyyy-MM-dd').format(widget.log.date),
      icon: Icons.fastfood,
      recommendation: _recommendation,
      onDelete: widget.onDelete, // Pass the callback through
      onEdit: widget.onEdit,     // Pass the callback through
    );
  }
}
