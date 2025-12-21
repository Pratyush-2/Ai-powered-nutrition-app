import 'package:flutter/material.dart';
import 'package:nutrition_app/models/goal.dart';
import 'package:nutrition_app/models/profile.dart';
import 'package:nutrition_app/screens/create_profile_screen.dart';
import 'package:nutrition_app/screens/edit_profile_screen.dart';
import 'package:nutrition_app/screens/set_goals_screen.dart';
import 'package:nutrition_app/services/api_client.dart';

class ProfileScreen extends StatefulWidget {
  final int userId;
  const ProfileScreen({super.key, required this.userId});

  @override
  State<ProfileScreen> createState() => _ProfileScreenState();
}

class _ProfileScreenState extends State<ProfileScreen> {
  late Future<Map<String, dynamic>> _dataFuture;

  @override
  void initState() {
    super.initState();
    _dataFuture = _getData();
  }

  Future<Map<String, dynamic>> _getData() async {
    final userProfileData = await apiService.getProfileById(widget.userId);
    final userProfile = UserProfileModel.fromJson(userProfileData);
    List<Goal> goals = [];
    try {
      goals = await apiService.getGoals(widget.userId);
    } catch (e) {
      // Handle the case where the user has no goals
      if (e.toString().contains('404')) {
        goals = [];
      } else {
        rethrow;
      }
    }
    return {
      'profiles': [userProfile],
      'goals': goals,
    };
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Profile'),
      ),
      body: FutureBuilder<Map<String, dynamic>>(
        future: _dataFuture,
        builder: (context, snapshot) {
          if (snapshot.connectionState == ConnectionState.waiting) {
            return const Center(child: CircularProgressIndicator());
          } else if (snapshot.hasError) {
            return Center(child: Text('Error: ${snapshot.error}'));
          } else if (snapshot.hasData) {
            final data = snapshot.data!;
            final profiles = data['profiles'] as List<UserProfileModel>;
            final goals = data['goals'] as List<Goal>;
            final userProfile = profiles.isNotEmpty ? profiles.first : null;
            final nutritionGoals = goals.isNotEmpty ? goals.first : null;

            if (userProfile == null) {
              return Center(
                child: ElevatedButton(
                  onPressed: () async {
                    final result = await Navigator.of(context).push(
                      MaterialPageRoute(builder: (_) => CreateProfileScreen()),
                    );
                    if (result == true) {
                      setState(() {
                        _dataFuture = _getData();
                      });
                    }
                  },
                  child: const Text('Create Profile'),
                ),
              );
            }

            return SingleChildScrollView(
              padding: const EdgeInsets.all(16.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Card(
                    elevation: 4,
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                    child: Padding(
                      padding: const EdgeInsets.all(16.0),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text('Personal Info', style: Theme.of(context).textTheme.headlineSmall),
                          const Divider(),
                          _buildInfoTile(Icons.person, 'Name', userProfile.name),
                          _buildInfoTile(Icons.cake, 'Age', userProfile.age.toString()),
                          _buildInfoTile(Icons.height, 'Height', '${userProfile.heightCm} cm'),
                          _buildInfoTile(Icons.line_weight, 'Weight', '${userProfile.weightKg} kg'),
                          _buildInfoTile(Icons.wc, 'Gender', userProfile.gender),
                          _buildInfoTile(Icons.fitness_center, 'Activity Level', userProfile.activityLevel),
                          _buildInfoTile(Icons.flag, 'Goal', userProfile.goal ?? 'N/A'),
                        ],
                      ),
                    ),
                  ),
                  const SizedBox(height: 20),
                  Card(
                    elevation: 4,
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                    child: Padding(
                      padding: const EdgeInsets.all(16.0),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text('Daily Nutrition Goals', style: Theme.of(context).textTheme.headlineSmall),
                          const Divider(),
                          _buildNutritionCard(nutritionGoals, context),
                        ],
                      ),
                    ),
                  ),
                  const SizedBox(height: 20),
                  ElevatedButton(
                    onPressed: () async {
                      final result = await Navigator.of(context).push(
                        MaterialPageRoute(
                          builder: (_) => EditProfileScreen(profile: userProfile),
                        ),
                      );
                      if (result == true) {
                        setState(() {
                          _dataFuture = _getData();
                        });
                      }
                    },
                    child: const Text('Edit Profile'),
                  ),
                  const SizedBox(height: 10),
                  ElevatedButton(
                    onPressed: () async {
                      final result = await Navigator.of(context).push(
                        MaterialPageRoute(
                          builder: (_) => SetGoalsScreen(userId: widget.userId),
                        ),
                      );
                      if (result == true) {
                        setState(() {
                          _dataFuture = _getData();
                        });
                      }
                    },
                    child: const Text('Set Goals'),
                  ),
                ],
              ),
            );
          }
          return const Center(child: Text('No profile data available.'));
        },
      ),
    );
  }

  Widget _buildInfoTile(IconData icon, String label, String value) {
    return ListTile(
      leading: Icon(icon, color: Theme.of(context).colorScheme.primary),
      title: Text(label),
      subtitle: Text(value, style: Theme.of(context).textTheme.bodyLarge),
    );
  }

  Widget _buildNutritionCard(Goal? nutrition, BuildContext context) {
    if (nutrition == null) {
      return const Text('No nutrition goals set.');
    }
    return Column(
      children: [
        _buildNutritionItem('Calories', nutrition.caloriesGoal.toString(), context),
        _buildNutritionItem('Protein', '${nutrition.proteinGoal} g', context),
        _buildNutritionItem('Fats', '${nutrition.fatsGoal} g', context),
        _buildNutritionItem('Carbs', '${nutrition.carbsGoal} g', context),
      ],
    );
  }

  Widget _buildNutritionItem(String label, String value, BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8.0),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(label, style: Theme.of(context).textTheme.titleMedium),
          Text(value, style: Theme.of(context).textTheme.titleMedium?.copyWith(fontWeight: FontWeight.bold)),
        ],
      ),
    );
  }
}
