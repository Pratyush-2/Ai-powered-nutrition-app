import 'package:flutter/material.dart';
import 'package:nutrition_app/models/goal.dart';
import 'package:nutrition_app/models/profile.dart';
import 'package:nutrition_app/screens/edit_profile_screen.dart';
import 'package:nutrition_app/screens/login_screen.dart';
import 'package:nutrition_app/screens/set_goals_screen.dart';
import 'package:nutrition_app/main.dart';

class ProfileScreen extends StatefulWidget {
  final bool isGuest;
  const ProfileScreen({super.key, this.isGuest = false});

  @override
  State<ProfileScreen> createState() => _ProfileScreenState();
}

class _ProfileScreenState extends State<ProfileScreen> {
  late Future<Map<String, dynamic>> _dataFuture;

  @override
  void initState() {
    super.initState();
    if (!widget.isGuest) {
      _dataFuture = _getData();
    }
  }

  Future<Map<String, dynamic>> _getData() async {
    final userProfileData = await apiService.getProfile();
    final userProfile = UserProfileModel.fromJson(userProfileData);
    List<Goal> goals = [];
    try {
      goals = await apiService.getGoals();
    } catch (e) {
      if (e.toString().contains('404')) {
        goals = [];
      } else {
        rethrow;
      }
    }
    return {
      'profile': userProfile,
      'goals': goals,
    };
  }

  Future<void> _logout() async {
    await apiService.logout();
    Navigator.of(context).pushAndRemoveUntil(
      MaterialPageRoute(builder: (context) => const LoginScreen()),
      (Route<dynamic> route) => false,
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(widget.isGuest ? 'Guest Profile' : 'Profile'),
        actions: [
          IconButton(
            icon: const Icon(Icons.logout),
            onPressed: _logout,
          ),
        ],
      ),
      body: widget.isGuest ? _buildGuestView() : FutureBuilder<Map<String, dynamic>>(
        future: _dataFuture,
        builder: (context, snapshot) {
          if (snapshot.connectionState == ConnectionState.waiting) {
            return const Center(child: CircularProgressIndicator());
          } else if (snapshot.hasError) {
            return Center(child: Text('Error: ${snapshot.error}'));
          } else if (snapshot.hasData) {
            final data = snapshot.data!;
            final userProfile = data['profile'] as UserProfileModel?;
            final goals = data['goals'] as List<Goal>;
            final nutritionGoals = goals.isNotEmpty ? goals.first : null;

            if (userProfile == null) {
              return const Center(child: Text('Could not load profile.'));
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
                          builder: (_) => SetGoalsScreen(),
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

  Widget _buildGuestView() {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(24.0),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              Icons.person_outline,
              size: 100,
              color: Colors.grey[400],
            ),
            const SizedBox(height: 24),
            Text(
              'Guest Mode',
              style: Theme.of(context).textTheme.headlineMedium?.copyWith(
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 16),
            Text(
              'You\'re using the app as a guest',
              style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                color: Colors.grey[600],
              ),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 8),
            Text(
              'Limited features available:\n• No data sync\n• No profile customization\n• No goal tracking',
              style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                color: Colors.grey[500],
              ),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 32),
            ElevatedButton.icon(
              onPressed: () {
                Navigator.of(context).pushAndRemoveUntil(
                  MaterialPageRoute(builder: (context) => const LoginScreen()),
                  (Route<dynamic> route) => false,
                );
              },
              icon: const Icon(Icons.login),
              label: const Text('Login or Register'),
              style: ElevatedButton.styleFrom(
                padding: const EdgeInsets.symmetric(horizontal: 32, vertical: 16),
              ),
            ),
            const SizedBox(height: 16),
            Text(
              'Create an account to unlock all features!',
              style: Theme.of(context).textTheme.bodySmall?.copyWith(
                color: Colors.grey[600],
                fontStyle: FontStyle.italic,
              ),
              textAlign: TextAlign.center,
            ),
          ],
        ),
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
