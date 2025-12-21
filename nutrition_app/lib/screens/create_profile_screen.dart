import 'dart:developer' as developer;
import 'package:connectivity_plus/connectivity_plus.dart';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'package:shared_preferences/shared_preferences.dart';
import 'main_tabs.dart';

class CreateProfileScreen extends StatefulWidget {
  CreateProfileScreen({super.key});

  @override
  State<CreateProfileScreen> createState() => _CreateProfileScreenState();
}

class _CreateProfileScreenState extends State<CreateProfileScreen> {
  final _formKey = GlobalKey<FormState>();
  final _nameController = TextEditingController();
  final _ageController = TextEditingController();
  final _weightController = TextEditingController();
  final _heightController = TextEditingController();
  final String? _gender = 'Male';
  final String? _activityLevel = 'Sedentary';
  final List<String> _selectedAllergies = [];
  final List<String> _selectedHealthConditions = [];
  final _fitnessGoalController = TextEditingController();
  bool _isLoading = false;

  void _showMultiSelect(
    BuildContext context,
    List<String> options,
    List<String> selectedItems,
    Function(List<String>) onConfirm,
  ) {
    showDialog(
      context: context,
      builder: (BuildContext context) {
        return AlertDialog(
          title: const Text('Select Items'),
          content: SingleChildScrollView(
            child: ListBody(
              children: options.map((item) {
                return CheckboxListTile(
                  value: selectedItems.contains(item),
                  title: Text(item),
                  onChanged: (isChecked) {
                    if (isChecked != null) {
                      if (isChecked) {
                        selectedItems.add(item);
                      } else {
                        selectedItems.remove(item);
                      }
                    }
                    (context as Element)
                        .markNeedsBuild(); // Rebuild to reflect changes
                  },
                );
              }).toList(),
            ),
          ),
          actions: <Widget>[
            TextButton(
              child: const Text('CANCEL'),
              onPressed: () {
                Navigator.pop(context);
              },
            ),
            TextButton(
              child: const Text('SELECT'),
              onPressed: () {
                onConfirm(selectedItems);
                Navigator.pop(context);
              },
            ),
          ],
        );
      },
    );
  }

  Future<void> _createProfile() async {
    developer.log('Attempting to create profile', name: 'CreateProfileScreen');
    if (_formKey.currentState!.validate()) {
      _formKey.currentState!.save();

      var connectivityResult = await (Connectivity().checkConnectivity());
      if (connectivityResult == ConnectivityResult.none) {
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(
              content: Text(
                'No internet connection. Please check your network settings.',
              ),
            ),
          );
        }
        return;
      }

      setState(() {
        _isLoading = true;
      });
    }

    try {
      final age = int.tryParse(_ageController.text);
      final weight = double.tryParse(_weightController.text);
      final height = double.tryParse(_heightController.text);

      if (age == null || weight == null || height == null) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text(
              'Please enter valid numbers for age, weight, and height.',
            ),
          ),
        );
        setState(() {
          _isLoading = false;
        });
        return;
      }
      final profileData = {
        'name': _nameController.text,
        'age': age,
        'weight_kg': weight,
        'height_cm': height,
        'gender': _gender,
        'activity_level': _activityLevel,
        'allergies': _selectedAllergies.join(', '),
        'health_conditions': _selectedHealthConditions.join(', '),
        'fitness_goal': _fitnessGoalController.text,
      };

      final response = await http.post(
        Uri.parse('http://10.0.2.2:8000/profiles/'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode(profileData),
      );

      if (response.statusCode == 200 && mounted) {
        final data = json.decode(response.body);
        final userId = data['id'];

        // Save the user ID to local storage
        final prefs = await SharedPreferences.getInstance();
        await prefs.setInt('user_id', userId);

        Navigator.of(context).pushReplacement(
          MaterialPageRoute(builder: (context) => MainTabs(userId: userId)),
        );
      } else {
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text(
                'Failed to create profile. Status: {response.statusCode}',
              ),
            ),
          );
        }
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(
          context,
        ).showSnackBar(SnackBar(content: Text('An error occurred: $e')));
      }
    } finally {
      if (mounted) {
        setState(() {
          _isLoading = false;
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Create Your Profile')),
      body: SafeArea(
        child: Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              // Removed all TextFormField widgets and ElevatedButton for debugging
            ],
          ),
        ),
      ),
    );
  }
}
