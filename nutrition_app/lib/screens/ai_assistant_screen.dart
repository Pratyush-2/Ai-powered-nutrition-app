import 'package:flutter/material.dart';

class AIAssistantScreen extends StatelessWidget {
  final int userId;

  const AIAssistantScreen({super.key, required this.userId});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('AI Assistant (Disabled)')),
      body: const Center(
        child: Text('AI Assistant screen is currently disabled.'),
      ),
    );
  }
}