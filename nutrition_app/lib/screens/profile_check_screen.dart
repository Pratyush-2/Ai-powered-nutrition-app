import 'package:flutter/material.dart';
import 'package:nutrition_app/screens/create_profile_screen.dart';
import 'package:nutrition_app/screens/main_tabs.dart';
import 'package:shared_preferences/shared_preferences.dart';

class ProfileCheckScreen extends StatefulWidget {
  const ProfileCheckScreen({super.key});

  @override
  State<ProfileCheckScreen> createState() => _ProfileCheckScreenState();
}

class _ProfileCheckScreenState extends State<ProfileCheckScreen> {
  @override
  void initState() {
    super.initState();
    _checkProfileStatus();
  }

  Future<void> _checkProfileStatus() async {
    final prefs = await SharedPreferences.getInstance();
    // Use `getInt` as user IDs are typically integers.
    final userId = prefs.getInt('user_id');

    // A short delay to prevent a jarring flash of the loading screen on fast devices.
    await Future.delayed(const Duration(milliseconds: 500));

    if (!mounted) return;

    if (userId != null) {
      // If user ID exists, go to the main app screen.
      Navigator.of(context).pushReplacement(
        MaterialPageRoute(builder: (context) => MainTabs(userId: userId)),
      );
    } else {
      // If no user ID, go to the profile creation screen.
      Navigator.of(context).pushReplacement(
        MaterialPageRoute(builder: (context) => CreateProfileScreen()),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    // Show a loading indicator while we check for the profile.
    return const Scaffold(
      body: Center(
        child: CircularProgressIndicator(),
      ),
    );
  }
}
