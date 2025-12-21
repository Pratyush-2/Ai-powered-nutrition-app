import 'package:flutter/material.dart';

class AIDetailsScreen extends StatelessWidget {
  final int userId;
  final int foodId;

  const AIDetailsScreen({super.key, required this.userId, required this.foodId});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('AI Details (Disabled)')),
      body: const Center(
        child: Text('AI Details screen is currently disabled.'),
      ),
    );
  }
}