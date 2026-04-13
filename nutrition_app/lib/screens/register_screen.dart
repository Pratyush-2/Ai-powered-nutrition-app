import 'dart:ui';
import 'package:flutter/material.dart';
import 'package:nutrition_app/main.dart';
import 'dart:developer' as developer;

class RegisterScreen extends StatefulWidget {
  const RegisterScreen({super.key});

  @override
  _RegisterScreenState createState() => _RegisterScreenState();
}

class _RegisterScreenState extends State<RegisterScreen> {
  final _formKey = GlobalKey<FormState>();
  String _email = '';
  String _password = '';
  String _name = '';
  int? _age;
  double? _weight;
  double? _height;
  String? _gender;
  String? _activityLevel;

  bool _isLoading = false;

  Future<void> _register() async {
    if (_formKey.currentState!.validate()) {
      _formKey.currentState!.save();
      setState(() => _isLoading = true);
      try {
        developer.log('Registering with password: $_password');
        await apiService.register({
          'name': _name,
          'email': _email,
          'password': _password,
          'age': _age,
          'weight_kg': _weight,
          'height_cm': _height,
          'gender': _gender,
          'activity_level': _activityLevel,
          'goal': 'maintain', // Default goal
        });
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Registration successful! Please login.'),
            backgroundColor: Colors.greenAccent,
            action: null,
          ),
        );
        Navigator.of(context).pop();
      } catch (e) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Failed to register: $e'),
            backgroundColor: Colors.redAccent,
          ),
        );
      } finally {
        setState(() => _isLoading = false);
      }
    }
  }

  Widget _buildTextField(String label, IconData icon, Function(String?) onSaved, {bool isNumber = false, bool isPassword = false, String? Function(String?)? validator}) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 16.0),
      child: TextFormField(
        style: const TextStyle(color: Colors.white),
        decoration: InputDecoration(
          labelText: label,
          labelStyle: TextStyle(color: Colors.white.withOpacity(0.5)),
          prefixIcon: Icon(icon, color: Colors.greenAccent),
          enabledBorder: OutlineInputBorder(
            borderSide: BorderSide(color: Colors.white.withOpacity(0.1)),
            borderRadius: BorderRadius.circular(12),
          ),
          focusedBorder: OutlineInputBorder(
            borderSide: const BorderSide(color: Colors.greenAccent),
            borderRadius: BorderRadius.circular(12),
          ),
          filled: true,
          fillColor: Colors.black.withOpacity(0.2),
        ),
        obscureText: isPassword,
        keyboardType: isNumber ? TextInputType.number : TextInputType.text,
        validator: validator ?? (value) => value == null || value.isEmpty ? 'Required field' : null,
        onSaved: onSaved,
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      extendBodyBehindAppBar: true,
      appBar: AppBar(
        title: const Text('Create Account', style: TextStyle(fontWeight: FontWeight.bold, color: Colors.white)),
        backgroundColor: Colors.transparent,
        elevation: 0,
        iconTheme: const IconThemeData(color: Colors.white),
      ),
      body: Container(
        height: double.infinity,
        decoration: const BoxDecoration(
          gradient: LinearGradient(
            colors: [Color(0xFF1B1D22), Color(0xFF2A2D34)],
            begin: Alignment.topRight,
            end: Alignment.bottomLeft,
          ),
        ),
        child: SafeArea(
          child: SingleChildScrollView(
            padding: const EdgeInsets.all(24.0),
            child: Column(
              children: [
                ClipRRect(
                  borderRadius: BorderRadius.circular(24),
                  child: BackdropFilter(
                    filter: ImageFilter.blur(sigmaX: 10, sigmaY: 10),
                    child: Container(
                      padding: const EdgeInsets.all(24),
                      decoration: BoxDecoration(
                        color: Colors.white.withOpacity(0.05),
                        borderRadius: BorderRadius.circular(24),
                        border: Border.all(
                          color: Colors.white.withOpacity(0.1),
                          width: 1.5,
                        ),
                      ),
                      child: Form(
                        key: _formKey,
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.stretch,
                          children: [
                            _buildTextField('Full Name', Icons.person_outline, (val) => _name = val!),
                            _buildTextField('Email', Icons.email_outlined, (val) => _email = val!, validator: (val) => val!.isEmpty ? 'Enter email' : null),
                            _buildTextField('Password', Icons.lock_outline, (val) => _password = val!, isPassword: true, validator: (val) => val!.length < 6 ? 'Min 6 chars' : null),
                            
                            Row(
                              children: [
                                Expanded(child: _buildTextField('Age', Icons.calendar_today, (val) => _age = int.tryParse(val ?? ''), isNumber: true)),
                                const SizedBox(width: 16),
                                Expanded(child: _buildTextField('Weight (kg)', Icons.scale, (val) => _weight = double.tryParse(val ?? ''), isNumber: true)),
                              ],
                            ),
                            
                            _buildTextField('Height (cm)', Icons.height, (val) => _height = double.tryParse(val ?? ''), isNumber: true),

                            // Gender Dropdown
                            Padding(
                              padding: const EdgeInsets.only(bottom: 16.0),
                              child: DropdownButtonFormField<String>(
                                dropdownColor: const Color(0xFF2A2D34),
                                style: const TextStyle(color: Colors.white),
                                decoration: InputDecoration(
                                  labelText: 'Gender',
                                  labelStyle: TextStyle(color: Colors.white.withOpacity(0.5)),
                                  prefixIcon: const Icon(Icons.people_outline, color: Colors.greenAccent),
                                  enabledBorder: OutlineInputBorder(
                                    borderSide: BorderSide(color: Colors.white.withOpacity(0.1)),
                                    borderRadius: BorderRadius.circular(12),
                                  ),
                                  focusedBorder: OutlineInputBorder(
                                    borderSide: const BorderSide(color: Colors.greenAccent),
                                    borderRadius: BorderRadius.circular(12),
                                  ),
                                  filled: true,
                                  fillColor: Colors.black.withOpacity(0.2),
                                ),
                                items: ['Male', 'Female']
                                    .map((label) => DropdownMenuItem(value: label, child: Text(label)))
                                    .toList(),
                                onChanged: (val) => setState(() => _gender = val),
                                onSaved: (val) => _gender = val,
                              ),
                            ),

                            // Activity Dropdown
                            Padding(
                              padding: const EdgeInsets.only(bottom: 24.0),
                              child: DropdownButtonFormField<String>(
                                dropdownColor: const Color(0xFF2A2D34),
                                style: const TextStyle(color: Colors.white),
                                decoration: InputDecoration(
                                  labelText: 'Activity Level',
                                  labelStyle: TextStyle(color: Colors.white.withOpacity(0.5)),
                                  prefixIcon: const Icon(Icons.directions_run, color: Colors.greenAccent),
                                  enabledBorder: OutlineInputBorder(
                                    borderSide: BorderSide(color: Colors.white.withOpacity(0.1)),
                                    borderRadius: BorderRadius.circular(12),
                                  ),
                                  focusedBorder: OutlineInputBorder(
                                    borderSide: const BorderSide(color: Colors.greenAccent),
                                    borderRadius: BorderRadius.circular(12),
                                  ),
                                  filled: true,
                                  fillColor: Colors.black.withOpacity(0.2),
                                ),
                                items: [
                                  'sedentary', 'lightly_active', 'moderately_active', 'very_active', 'super_active'
                                ]
                                    .map((label) => DropdownMenuItem(value: label, child: Text(label.replaceAll('_', ' '))))
                                    .toList(),
                                onChanged: (val) => setState(() => _activityLevel = val),
                                onSaved: (val) => _activityLevel = val,
                              ),
                            ),

                            _isLoading
                                ? const Center(child: CircularProgressIndicator(color: Colors.greenAccent))
                                : ElevatedButton(
                                    onPressed: _register,
                                    style: ElevatedButton.styleFrom(
                                      backgroundColor: Colors.greenAccent,
                                      foregroundColor: Colors.black87,
                                      padding: const EdgeInsets.symmetric(vertical: 16),
                                      shape: RoundedRectangleBorder(
                                        borderRadius: BorderRadius.circular(12),
                                      ),
                                      elevation: 0,
                                    ),
                                    child: const Text('Register', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
                                  ),
                          ],
                        ),
                      ),
                    ),
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
