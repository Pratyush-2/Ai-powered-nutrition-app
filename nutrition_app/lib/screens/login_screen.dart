import 'dart:ui';
import 'package:flutter/material.dart';
import 'package:nutrition_app/screens/main_tabs.dart';
import 'package:nutrition_app/screens/register_screen.dart';
import 'package:nutrition_app/main.dart';
import 'package:nutrition_app/theme/app_theme.dart';
import 'package:nutrition_app/widgets/glass_card.dart';
import 'package:google_sign_in/google_sign_in.dart';

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

  Future<void> _googleLogin() async {
    setState(() => _isGoogleLoading = true);
    try {
      // NOTE: For Web, you MUST provide a clientId.
      // Replace this string with your Google Cloud Web Client ID
      final GoogleSignIn googleSignIn = GoogleSignIn(
        clientId: 'YOUR_CLIENT_ID_HERE.apps.googleusercontent.com',
      );
      
      final GoogleSignInAccount? googleUser = await googleSignIn.signIn();
      
      if (googleUser == null) {
        // User canceled
        return;
      }
      
      final GoogleSignInAuthentication googleAuth = await googleUser.authentication;
      final String? idToken = googleAuth.idToken;
      
      if (idToken == null) {
        throw Exception("Failed to get ID token");
      }
      
      // Call our backend
      await apiService.googleLogin(idToken);
      
      if (mounted) {
        Navigator.of(context).pushReplacement(
          MaterialPageRoute(builder: (context) => const MainTabs()),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Google Login failed: $e')),
        );
      }
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
            colors: [AppTheme.background, Color(0xFF000000)],
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

                  GlassCard(
                    padding: const EdgeInsets.all(24),
                    child: Form(
                      key: _formKey,
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.stretch,
                        children: [
                          TextFormField(
                            style: TextStyle(color: AppTheme.textPrimary),
                            decoration: InputDecoration(
                              labelText: 'Email',
                              prefixIcon: Icon(Icons.email_outlined, color: AppTheme.primary),
                            ),
                            keyboardType: TextInputType.emailAddress,
                            validator: (value) =>
                                value!.isEmpty ? 'Please enter your email' : null,
                            onSaved: (value) => _email = value!,
                          ),
                          const SizedBox(height: 16),
                          TextFormField(
                            style: TextStyle(color: AppTheme.textPrimary),
                            decoration: InputDecoration(
                              labelText: 'Password',
                              prefixIcon: Icon(Icons.lock_outline, color: AppTheme.primary),
                            ),
                            obscureText: true,
                            validator: (value) =>
                                value!.isEmpty ? 'Please enter your password' : null,
                            onSaved: (value) => _password = value!,
                          ),
                          const SizedBox(height: 24),
                          
                          _isLoading
                              ? Center(child: CircularProgressIndicator(color: AppTheme.primary))
                              : ElevatedButton(
                                  onPressed: _login,
                                  child: const Text('Sign In'),
                                ),
                        ],
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
                          onPressed: _googleLogin,
                          icon: Image.network(
                            'https://upload.wikimedia.org/wikipedia/commons/thumb/c/c1/Google_%22G%22_logo.svg/120px-Google_%22G%22_logo.svg.png',
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
