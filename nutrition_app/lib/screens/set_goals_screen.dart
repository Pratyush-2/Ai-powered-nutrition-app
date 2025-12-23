import 'package:flutter/material.dart';
import 'package:nutrition_app/main.dart';
import 'package:nutrition_app/models/profile.dart';
import 'package:nutrition_app/models/goal.dart';
import 'dart:developer' as developer;

class SetGoalsScreen extends StatefulWidget {
  const SetGoalsScreen({super.key});

  @override
  State<SetGoalsScreen> createState() => _SetGoalsScreenState();
}

class _SetGoalsScreenState extends State<SetGoalsScreen> {
  UserProfileModel? _userProfile;
  Goal? _currentGoals;
  bool _isLoading = true;
  String? _selectedActivityLevel;
  String? _selectedGoalType; // e.g., 'Maintain', 'Lose', 'Gain'
  double _weightChangePerWeek = 0.5; // kg per week

  final TextEditingController _targetWeightController = TextEditingController();

  double _calculatedCalories = 0.0;
  double _calculatedProtein = 0.0;
  double _calculatedCarbs = 0.0;
  double _calculatedFats = 0.0;

  // Activity level mapping between backend and frontend
  static const Map<String, String> _activityLevelMapping = {
    'sedentary': 'Sedentary',
    'lightly_active': 'Lightly Active',
    'moderately_active': 'Moderately Active',
    'very_active': 'Very Active',
    'super_active': 'Extra Active',
  };

  static const Map<String, String> _reverseActivityMapping = {
    'Sedentary': 'sedentary',
    'Lightly Active': 'lightly_active',
    'Moderately Active': 'moderately_active',
    'Very Active': 'very_active',
    'Extra Active': 'super_active',
  };

  @override
  void initState() {
    super.initState();
    _fetchUserData();
  }

  @override
  void dispose() {
    _targetWeightController.dispose();
    super.dispose();
  }

  Future<void> _fetchUserData() async {
    try {
      final profileData = await apiService.getProfile();
      _userProfile = UserProfileModel.fromJson(profileData);

      final goals = await apiService.getGoals();
      if (goals.isNotEmpty) {
        _currentGoals = goals.first;
      }

      setState(() {
        _isLoading = false;
        // Convert backend activity level to frontend display format
        _selectedActivityLevel = _activityLevelMapping[_userProfile?.activityLevel] ?? 'Sedentary';
        _selectedGoalType = _currentGoals != null ? _getGoalTypeFromGoals(_currentGoals!) : 'Maintain';
        if (_currentGoals != null) {
          _calculatedCalories = _currentGoals!.caloriesGoal;
          _calculatedProtein = _currentGoals!.proteinGoal;
          _calculatedCarbs = _currentGoals!.carbsGoal;
          _calculatedFats = _currentGoals!.fatsGoal;
        }
        _calculateGoals(); // Calculate initial goals based on fetched data
      });
    } catch (e) {
      developer.log('Error fetching user data: $e');
      setState(() {
        _isLoading = false;
        // Set default value if there's an error
        _selectedActivityLevel = 'Sedentary';
      });
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Failed to load user data: $e')),
      );
    }
  }

  String _getGoalTypeFromGoals(Goal goals) {
    // Simple logic to infer goal type from current goals
    // This might need more sophisticated logic based on how goals are set in the backend
    if (goals.caloriesGoal > 2500) return 'Gain'; // Arbitrary threshold
    if (goals.caloriesGoal < 1800) return 'Lose'; // Arbitrary threshold
    return 'Maintain';
  }

  void _calculateGoals() {
    if (_userProfile == null) return;

    // Mifflin-St Jeor Equation for BMR
    double bmr;
    if (_userProfile!.gender == 'Male') {
      bmr = (10 * _userProfile!.weightKg) + (6.25 * _userProfile!.heightCm) - (5 * _userProfile!.age) + 5;
    } else {
      bmr = (10 * _userProfile!.weightKg) + (6.25 * _userProfile!.heightCm) - (5 * _userProfile!.age) - 161;
    }

    // TDEE (Total Daily Energy Expenditure) based on activity level
    double activityMultiplier;
    switch (_selectedActivityLevel) {
      case 'Sedentary':
        activityMultiplier = 1.2;
        break;
      case 'Lightly Active':
        activityMultiplier = 1.375;
        break;
      case 'Moderately Active':
        activityMultiplier = 1.55;
        break;
      case 'Very Active':
        activityMultiplier = 1.725;
        break;
      case 'Extra Active':
        activityMultiplier = 1.9;
        break;
      default:
        activityMultiplier = 1.2;
    }

    double tdee = bmr * activityMultiplier;

    // Adjust for weight goal
    double calorieAdjustment = 0;
    if (_selectedGoalType == 'Lose') {
      calorieAdjustment = -(_weightChangePerWeek * 7700 / 7); // 7700 calories per kg
    } else if (_selectedGoalType == 'Gain') {
      calorieAdjustment = (_weightChangePerWeek * 7700 / 7);
    }

    _calculatedCalories = tdee + calorieAdjustment;

    // Macro distribution (example percentages, can be customized)
    // Protein: 25-30% of calories
    // Fats: 20-25% of calories
    // Carbs: Remaining
    _calculatedProtein = (_calculatedCalories * 0.25) / 4; // 4 kcal/g protein
    _calculatedFats = (_calculatedCalories * 0.25) / 9; // 9 kcal/g fat
    _calculatedCarbs = (_calculatedCalories - (_calculatedProtein * 4) - (_calculatedFats * 9)) / 4; // 4 kcal/g carbs

    setState(() {});
  }

  Future<void> _saveGoals() async {
    if (_userProfile == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('User profile not loaded. Cannot save goals.')),
      );
      return;
    }

    setState(() {
      _isLoading = true;
    });

    try {
      final goalData = {
        'calories_goal': _calculatedCalories.round(),
        'protein_goal': _calculatedProtein.round(),
        'carbs_goal': _calculatedCarbs.round(),
        'fats_goal': _calculatedFats.round(),
        'target_weight_kg': double.tryParse(_targetWeightController.text) ?? _userProfile!.weightKg,
        'goal_type': _selectedGoalType,
        'weight_change_per_week': _weightChangePerWeek,
      };

      // Convert frontend activity level back to backend format
      final backendActivityLevel = _reverseActivityMapping[_selectedActivityLevel!] ?? 'sedentary';
      goalData['activity_level'] = backendActivityLevel;

      await apiService.setUserGoal(goalData); // Assuming this method handles creation/update
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Goals saved successfully!')),
      );
      Navigator.of(context).pop(true); // Go back and indicate success
    } catch (e) {
      developer.log('Error saving goals: $e');
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Failed to save goals: $e')),
      );
    } finally {
      setState(() {
        _isLoading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Set Your Goals'),
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : SingleChildScrollView(
              padding: const EdgeInsets.all(16.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'Current Profile:',
                    style: Theme.of(context).textTheme.headlineSmall,
                  ),
                  if (_userProfile != null)
                    Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text('Name: ${_userProfile!.name}'),
                        Text('Age: ${_userProfile!.age}'),
                        Text('Weight: ${_userProfile!.weightKg} kg'),
                        Text('Height: ${_userProfile!.heightCm} cm'),
                        Text('Gender: ${_userProfile!.gender}'),
                      ],
                    ),
                  const SizedBox(height: 20),
                  Text(
                    'Activity Level:',
                    style: Theme.of(context).textTheme.titleMedium,
                  ),
                  DropdownButton<String>(
                    value: _selectedActivityLevel,
                    onChanged: (String? newValue) {
                      setState(() {
                        _selectedActivityLevel = newValue;
                        _calculateGoals();
                      });
                    },
                    items: <String>[
                      'Sedentary',
                      'Lightly Active',
                      'Moderately Active',
                      'Very Active',
                      'Extra Active'
                    ].map<DropdownMenuItem<String>>((String value) {
                      return DropdownMenuItem<String>(
                        value: value,
                        child: Text(value),
                      );
                    }).toList(),
                  ),
                  const SizedBox(height: 20),
                  Text(
                    'Weight Goal:',
                    style: Theme.of(context).textTheme.titleMedium,
                  ),
                  DropdownButton<String>(
                    value: _selectedGoalType,
                    onChanged: (String? newValue) {
                      setState(() {
                        _selectedGoalType = newValue;
                        _calculateGoals();
                      });
                    },
                    items: <String>[
                      'Maintain',
                      'Lose',
                      'Gain',
                    ].map<DropdownMenuItem<String>>((String value) {
                      return DropdownMenuItem<String>(
                        value: value,
                        child: Text(value),
                      );
                    }).toList(),
                  ),
                  if (_selectedGoalType != 'Maintain') ...[
                    const SizedBox(height: 20),
                    Text(
                      'Weight Change per Week (kg):',
                      style: Theme.of(context).textTheme.titleMedium,
                    ),
                    Slider(
                      value: _weightChangePerWeek,
                      min: 0.1,
                      max: 1.0,
                      divisions: 9,
                      label: _weightChangePerWeek.toStringAsFixed(1),
                      onChanged: (double value) {
                        setState(() {
                          _weightChangePerWeek = value;
                          _calculateGoals();
                        });
                      },
                    ),
                    const SizedBox(height: 20),
                    TextFormField(
                      controller: _targetWeightController,
                      keyboardType: TextInputType.number,
                      decoration: const InputDecoration(
                        labelText: 'Target Weight (kg)',
                        border: OutlineInputBorder(),
                      ),
                      onChanged: (_) => _calculateGoals(),
                    ),
                  ],
                  const SizedBox(height: 30),
                  Text(
                    'Calculated Daily Goals:',
                    style: Theme.of(context).textTheme.headlineSmall,
                  ),
                  const SizedBox(height: 10),
                  _buildGoalDisplay('Calories', _calculatedCalories.round()),
                  _buildGoalDisplay('Protein', _calculatedProtein.round(), 'g'),
                  _buildGoalDisplay('Carbs', _calculatedCarbs.round(), 'g'),
                  _buildGoalDisplay('Fats', _calculatedFats.round(), 'g'),
                  const SizedBox(height: 30),
                  ElevatedButton(
                    onPressed: _isLoading ? null : _saveGoals,
                    child: _isLoading
                        ? const CircularProgressIndicator(color: Colors.white)
                        : const Text('Save Goals'),
                  ),
                ],
              ),
            ),
    );
  }

  Widget _buildGoalDisplay(String label, int value, [String unit = 'kcal']) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4.0),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(label, style: Theme.of(context).textTheme.titleMedium),
          Text('$value $unit', style: Theme.of(context).textTheme.titleLarge?.copyWith(fontWeight: FontWeight.bold)),
        ],
      ),
    );
  }
}
