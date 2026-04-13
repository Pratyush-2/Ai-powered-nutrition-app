import 'dart:ui';
import 'package:flutter/material.dart';
import 'package:nutrition_app/screens/main_tabs.dart';
import 'package:nutrition_app/screens/register_screen.dart';
import 'package:nutrition_app/main.dart';

class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key});

  @override
  _LoginScreenState createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final _formKey = GlobalKey<FormState>();
  String _email = '';
  String _password = '';
  bool _isLoading = false;
  bool _isGoogleLoading = false;

  Future<void> _login() async {
    if (_formKey.currentState!.validate()) {
      _formKey.currentState!.save();
      setState(() => _isLoading = true);
      try {
        await apiService.login(_email, _password);
        Navigator.of(context).pushReplacement(
          MaterialPageRoute(builder: (context) => const MainTabs()),
        );
      } catch (e) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Failed to login: $e'),
            backgroundColor: Colors.redAccent,
          ),
        );
      } finally {
        setState(() => _isLoading = false);
      }
    }
  }

  Future<void> _mockGoogleLogin() async {
    setState(() => _isGoogleLoading = true);
    try {
      // Simulating Google OAuth one-tap delay perfectly for recruiters
      await Future.delayed(const Duration(milliseconds: 1500));
      
      // Auto register/login using Mock OAuth Endpoint
      await apiService.mockOAuthLogin(
        'recruiter_demo@gmail.com', 
        'Recruiter Demo Account'
      );
      
      Navigator.of(context).pushReplacement(
        MaterialPageRoute(builder: (context) => const MainTabs()),
      );
    } catch (e) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Google Login failed: $e')),
        );
    } finally {
      if (mounted) setState(() => _isGoogleLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Container(
        decoration: const BoxDecoration(
          gradient: LinearGradient(
            colors: [Color(0xFF2A2D34), Color(0xFF1B1D22)],
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
          ),
        ),
        child: Center(
          child: SingleChildScrollView(
            child: Padding(
              padding: const EdgeInsets.symmetric(horizontal: 24.0),
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  // App Icon / Logo
                  Container(
                    padding: const EdgeInsets.all(16),
                    decoration: BoxDecoration(
                      color: Colors.greenAccent.withOpacity(0.1),
                      shape: BoxShape.circle,
                    ),
                    child: const Icon(
                      Icons.eco_rounded,
                      size: 80,
                      color: Colors.greenAccent,
                    ),
                  ),
                  const SizedBox(height: 24),
                  
                  const Text(
                    "Welcome Back",
                    style: TextStyle(
                      fontSize: 32,
                      fontWeight: FontWeight.bold,
                      color: Colors.white,
                      letterSpacing: 1.2,
                    ),
                  ),
                  const SizedBox(height: 8),
                  Text(
                    "Sign in to continue your health journey",
                    style: TextStyle(
                      fontSize: 14,
                      color: Colors.white.withOpacity(0.7),
                    ),
                  ),
                  const SizedBox(height: 48),

                  // Glassmorphism Card
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
                              TextFormField(
                                style: const TextStyle(color: Colors.white),
                                decoration: InputDecoration(
                                  labelText: 'Email',
                                  labelStyle: TextStyle(color: Colors.white.withOpacity(0.5)),
                                  prefixIcon: const Icon(Icons.email_outlined, color: Colors.greenAccent),
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
                                keyboardType: TextInputType.emailAddress,
                                validator: (value) =>
                                    value!.isEmpty ? 'Please enter your email' : null,
                                onSaved: (value) => _email = value!,
                              ),
                              const SizedBox(height: 16),
                              TextFormField(
                                style: const TextStyle(color: Colors.white),
                                decoration: InputDecoration(
                                  labelText: 'Password',
                                  labelStyle: TextStyle(color: Colors.white.withOpacity(0.5)),
                                  prefixIcon: const Icon(Icons.lock_outline, color: Colors.greenAccent),
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
                                obscureText: true,
                                validator: (value) =>
                                    value!.isEmpty ? 'Please enter your password' : null,
                                onSaved: (value) => _password = value!,
                              ),
                              const SizedBox(height: 24),
                              
                              _isLoading
                                  ? const Center(child: CircularProgressIndicator(color: Colors.greenAccent))
                                  : ElevatedButton(
                                      onPressed: _login,
                                      style: ElevatedButton.styleFrom(
                                        backgroundColor: Colors.greenAccent,
                                        foregroundColor: Colors.black87,
                                        padding: const EdgeInsets.symmetric(vertical: 16),
                                        shape: RoundedRectangleBorder(
                                          borderRadius: BorderRadius.circular(12),
                                        ),
                                        elevation: 0,
                                      ),
                                      child: const Text(
                                        'Sign In',
                                        style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                                      ),
                                    ),
                            ],
                          ),
                        ),
                      ),
                    ),
                  ),

                  const SizedBox(height: 24),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Container(height: 1, width: 60, color: Colors.white.withOpacity(0.2)),
                      Padding(
                        padding: const EdgeInsets.symmetric(horizontal: 12),
                        child: Text(
                          "OR",
                          style: TextStyle(color: Colors.white.withOpacity(0.5), fontWeight: FontWeight.bold),
                        ),
                      ),
                      Container(height: 1, width: 60, color: Colors.white.withOpacity(0.2)),
                    ],
                  ),
                  const SizedBox(height: 24),

                  // Mock Google Login Button
                  _isGoogleLoading
                      ? const Center(child: CircularProgressIndicator(color: Colors.white))
                      : OutlinedButton.icon(
                          onPressed: _mockGoogleLogin,
                          icon: Image.network(
                            'https://upload.wikimedia.org/wikipedia/commons/archive/c/c1/20230822192910%21Google_%22G%22_logo.svg',
                            height: 24,
                            width: 24,
                          ),
                          label: const Text(
                            'Continue with Google',
                            style: TextStyle(fontSize: 16, fontWeight: FontWeight.w600, color: Colors.white),
                          ),
                          style: OutlinedButton.styleFrom(
                            padding: const EdgeInsets.symmetric(vertical: 14, horizontal: 24),
                            shape: RoundedRectangleBorder(
                              borderRadius: BorderRadius.circular(12),
                            ),
                            side: BorderSide(color: Colors.white.withOpacity(0.2), width: 1.5),
                            backgroundColor: Colors.white.withOpacity(0.05),
                          ),
                        ),
                  
                  const SizedBox(height: 32),
                  
                  TextButton(
                    onPressed: () {
                      Navigator.push(
                        context,
                        MaterialPageRoute(builder: (context) => const RegisterScreen()),
                      );
                    },
                    child: RichText(
                      text: TextSpan(
                        text: "Don't have an account? ",
                        style: TextStyle(color: Colors.white.withOpacity(0.7)),
                        children: const [
                          TextSpan(
                            text: 'Sign up now',
                            style: TextStyle(color: Colors.greenAccent, fontWeight: FontWeight.bold),
                          ),
                        ],
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
}
