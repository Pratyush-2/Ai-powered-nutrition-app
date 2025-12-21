import 'package:flutter/material.dart';
import 'package:nutrition_app/models/profile.dart';
import 'package:nutrition_app/services/api_client.dart';
import 'dart:developer' as developer;

class EditProfileScreen extends StatefulWidget {
  final UserProfileModel profile;

  const EditProfileScreen({super.key, required this.profile});

  @override
  State<EditProfileScreen> createState() => _EditProfileScreenState();
}

class _EditProfileScreenState extends State<EditProfileScreen> {
  final _formKey = GlobalKey<FormState>();
  late TextEditingController _nameCtrl;
  late TextEditingController _ageCtrl;
  late TextEditingController _heightCtrl;
  late TextEditingController _weightCtrl;
  late TextEditingController _genderCtrl;
  late TextEditingController _activityCtrl;
  late TextEditingController _goalCtrl;
  bool _saving = false;

  @override
  void initState() {
    super.initState();
    _nameCtrl = TextEditingController(text: widget.profile.name);
    _ageCtrl = TextEditingController(text: widget.profile.age.toString());
    _heightCtrl = TextEditingController(text: widget.profile.heightCm.toString());
    _weightCtrl = TextEditingController(text: widget.profile.weightKg.toString());
    _genderCtrl = TextEditingController(text: widget.profile.gender);
    _activityCtrl = TextEditingController(text: widget.profile.activityLevel);
    _goalCtrl = TextEditingController(text: widget.profile.goal ?? '');
  }

  @override
  void dispose() {
    _nameCtrl.dispose();
    _ageCtrl.dispose();
    _heightCtrl.dispose();
    _weightCtrl.dispose();
    _genderCtrl.dispose();
    _activityCtrl.dispose();
    _goalCtrl.dispose();
    super.dispose();
  }

  Future<void> _saveProfile() async {
    if (_formKey.currentState!.validate()) {
      setState(() => _saving = true);
      try {
        final updatedModel = UserProfileModel(
          id: widget.profile.id,
          name: _nameCtrl.text,
          age: double.tryParse(_ageCtrl.text) ?? widget.profile.age,
          heightCm: double.tryParse(_heightCtrl.text) ?? widget.profile.heightCm,
          weightKg: double.tryParse(_weightCtrl.text) ?? widget.profile.weightKg,
          gender: _genderCtrl.text,
          activityLevel: _activityCtrl.text,
          goal: _goalCtrl.text,
        );
        final updated = await apiService.updateProfile(updatedModel.toJson());
        developer.log('Profile updated: $updated');
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Profile saved')));
          Navigator.of(context).pop(true); // Return true to indicate success
        }
      } catch (e) {
        developer.log('Update profile error: $e');
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Failed to save profile')));
        }
      } finally {
        if (mounted) {
          setState(() => _saving = false);
        }
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Edit Profile'),
        actions: [
          IconButton(
            onPressed: _saving ? null : _saveProfile,
            icon: _saving ? const SizedBox(height: 20, width: 20, child: CircularProgressIndicator(strokeWidth: 2)) : const Icon(Icons.save),
          ),
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16.0),
        child: Form(
          key: _formKey,
          child: Column(
            children: [
              TextFormField(
                controller: _nameCtrl,
                decoration: const InputDecoration(labelText: 'Name'),
                validator: (value) => value!.isEmpty ? 'Please enter a name' : null,
              ),
              TextFormField(
                controller: _ageCtrl,
                decoration: const InputDecoration(labelText: 'Age'),
                keyboardType: TextInputType.number,
                validator: (value) => value!.isEmpty ? 'Please enter an age' : null,
              ),
              TextFormField(
                controller: _heightCtrl,
                decoration: const InputDecoration(labelText: 'Height (cm)'),
                keyboardType: TextInputType.number,
                validator: (value) => value!.isEmpty ? 'Please enter a height' : null,
              ),
              TextFormField(
                controller: _weightCtrl,
                decoration: const InputDecoration(labelText: 'Weight (kg)'),
                keyboardType: TextInputType.number,
                validator: (value) => value!.isEmpty ? 'Please enter a weight' : null,
              ),
              TextFormField(
                controller: _genderCtrl,
                decoration: const InputDecoration(labelText: 'Gender'),
                validator: (value) => value!.isEmpty ? 'Please enter a gender' : null,
              ),
              TextFormField(
                controller: _activityCtrl,
                decoration: const InputDecoration(labelText: 'Activity Level'),
                validator: (value) => value!.isEmpty ? 'Please enter an activity level' : null,
              ),
              TextFormField(
                controller: _goalCtrl,
                decoration: const InputDecoration(labelText: 'Goal'),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
